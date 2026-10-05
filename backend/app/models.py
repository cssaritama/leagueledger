from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Match(Base):
    """A played match.

    Stored as a fact and never mutated. To correct a result you delete the
    match and record it again, which keeps the standings honest: there is no
    way for the table to disagree with the results behind it.
    """

    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("home_goals >= 0", name="home_goals_non_negative"),
        CheckConstraint("away_goals >= 0", name="away_goals_non_negative"),
        CheckConstraint("home_team_id != away_team_id", name="teams_must_differ"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    home_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    away_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    played_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    home_team: Mapped[Team] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped[Team] = relationship(foreign_keys=[away_team_id])
