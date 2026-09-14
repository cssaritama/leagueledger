from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Match, Team
from app.schemas import MatchCreate, MatchOut, StandingOut, TeamCreate, TeamOut
from app.standings import MatchResult, compute_standings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeagueLedger API",
    version="1.0.0",
    description=(
        "Matches are recorded as immutable facts. The league table is derived "
        "from them on every read and is never stored."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


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
    return [_to_match_out(m) for m in matches]


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
    """Recompute the table from the recorded matches.

    Nothing here is cached. The endpoint is a thin adapter around the pure
    function in app.standings, which holds all the league rules.
    """
    teams = [t.name for t in db.scalars(select(Team)).all()]
    matches = [
        MatchResult(
            home_team=m.home_team.name,
            away_team=m.away_team.name,
            home_goals=m.home_goals,
            away_goals=m.away_goals,
        )
        for m in db.scalars(select(Match)).all()
    ]

    table = compute_standings(teams, matches)

    return [
        StandingOut(
            position=index,
            team=s.team,
            played=s.played,
            won=s.won,
            drawn=s.drawn,
            lost=s.lost,
            goals_for=s.goals_for,
            goals_against=s.goals_against,
            goal_difference=s.goal_difference,
            points=s.points,
        )
        for index, s in enumerate(table, start=1)
    ]
