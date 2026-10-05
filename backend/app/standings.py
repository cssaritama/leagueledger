"""Standings engine.

This module is deliberately free of I/O. It knows nothing about HTTP,
SQLAlchemy or the database. It takes plain data in and returns plain data out,
which means the league rules can be tested without spinning up anything.

Standings are never stored. They are derived from matches on every read, so
the table can never drift out of sync with the results it claims to summarise.
"""

from dataclasses import dataclass

POINTS_WIN = 3
POINTS_DRAW = 1
POINTS_LOSS = 0


@dataclass(frozen=True)
class MatchResult:
    """A played match. Immutable by design: results are facts, not state."""

    home_team: str
    away_team: str
    home_goals: int
    away_goals: int


@dataclass
class TeamStanding:
    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.won * POINTS_WIN + self.drawn * POINTS_DRAW


def _record(standing: TeamStanding, scored: int, conceded: int) -> None:
    standing.played += 1
    standing.goals_for += scored
    standing.goals_against += conceded

    if scored > conceded:
        standing.won += 1
    elif scored == conceded:
        standing.drawn += 1
    else:
        standing.lost += 1


def compute_standings(
    teams: list[str], matches: list[MatchResult]
) -> list[TeamStanding]:
    """Build the league table from the full list of played matches.

    Every team appears in the table, including those who have not played yet.

    Tie-breakers, applied in order:
      1. points (descending)
      2. goal difference (descending)
      3. goals scored (descending)
      4. team name (alphabetical) - so the order is deterministic and a
         refresh never reshuffles teams that are genuinely level
    """
    table = {team: TeamStanding(team=team) for team in teams}

    for match in matches:
        if match.home_team not in table or match.away_team not in table:
            raise ValueError(
                f"Match references an unknown team: "
                f"{match.home_team} vs {match.away_team}"
            )
        _record(table[match.home_team], match.home_goals, match.away_goals)
        _record(table[match.away_team], match.away_goals, match.home_goals)

    return sorted(
        table.values(),
        key=lambda s: (-s.points, -s.goal_difference, -s.goals_for, s.team),
    )
