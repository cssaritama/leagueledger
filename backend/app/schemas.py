from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MatchCreate(BaseModel):
    home_team_id: int
    away_team_id: int
    home_goals: int = Field(ge=0, le=99)
    away_goals: int = Field(ge=0, le=99)


class MatchOut(BaseModel):
    id: int
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    played_at: datetime


class StandingOut(BaseModel):
    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
