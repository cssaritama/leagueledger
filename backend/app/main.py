from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION, AUTO_CREATE_SCHEMA, CORS_ORIGINS
from app.db import get_db, init_db
from app.models import Match, Team
from app.schemas import MatchCreate, MatchOut, StandingOut, TeamCreate, TeamOut
from app.standings import MatchResult, compute_standings


@asynccontextmanager
async def lifespan(_: FastAPI):
    if AUTO_CREATE_SCHEMA:
        init_db()
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Football competition API where match results are the source of truth "
        "and standings are derived on every read."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health():
    """Liveness probe: the process is running."""
    return {"status": "ok"}


@app.get("/ready", tags=["meta"])
def readiness(db: Session = Depends(get_db)):
    """Readiness probe: the application can reach its database."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - depends on external DB failure
        raise HTTPException(status_code=503, detail="Database is not ready") from exc
    return {"status": "ready"}


# --- Teams -----------------------------------------------------------------


@app.get("/teams", response_model=list[TeamOut], tags=["teams"])
def list_teams(db: Session = Depends(get_db)):
    return db.scalars(select(Team).order_by(Team.name)).all()


@app.post(
    "/teams",
    response_model=TeamOut,
    status_code=status.HTTP_201_CREATED,
    tags=["teams"],
)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Team name cannot be blank")

    existing = db.scalar(select(Team).where(Team.name == name))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Team already exists")

    team = Team(name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


# --- Matches ---------------------------------------------------------------


def _to_match_out(match: Match) -> MatchOut:
    return MatchOut(
        id=match.id,
        home_team=match.home_team.name,
        away_team=match.away_team.name,
        home_goals=match.home_goals,
        away_goals=match.away_goals,
        played_at=match.played_at,
    )


@app.get("/matches", response_model=list[MatchOut], tags=["matches"])
def list_matches(db: Session = Depends(get_db)):
    matches = db.scalars(
        select(Match).order_by(Match.played_at.desc(), Match.id.desc())
    ).all()
    return [_to_match_out(match) for match in matches]


@app.post(
    "/matches",
    response_model=MatchOut,
    status_code=status.HTTP_201_CREATED,
    tags=["matches"],
)
def create_match(payload: MatchCreate, db: Session = Depends(get_db)):
    if payload.home_team_id == payload.away_team_id:
        raise HTTPException(status_code=422, detail="A team cannot play itself")

    home = db.get(Team, payload.home_team_id)
    away = db.get(Team, payload.away_team_id)
    if home is None or away is None:
        raise HTTPException(status_code=404, detail="Team not found")

    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        home_goals=payload.home_goals,
        away_goals=payload.away_goals,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return _to_match_out(match)


@app.delete(
    "/matches/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["matches"],
)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()


# --- Standings (derived, never stored) -------------------------------------


@app.get("/standings", response_model=list[StandingOut], tags=["standings"])
def get_standings(db: Session = Depends(get_db)):
    teams = [team.name for team in db.scalars(select(Team)).all()]
    matches = [
        MatchResult(
            home_team=match.home_team.name,
            away_team=match.away_team.name,
            home_goals=match.home_goals,
            away_goals=match.away_goals,
        )
        for match in db.scalars(select(Match)).all()
    ]

    table = compute_standings(teams, matches)

    return [
        StandingOut(
            position=index,
            team=standing.team,
            played=standing.played,
            won=standing.won,
            drawn=standing.drawn,
            lost=standing.lost,
            goals_for=standing.goals_for,
            goals_against=standing.goals_against,
            goal_difference=standing.goal_difference,
            points=standing.points,
        )
        for index, standing in enumerate(table, start=1)
    ]
