# LeagueLedger - Product Specification

## Problem

Amateur and semi-pro leagues track results in spreadsheets. Someone enters a
score, someone else updates the table by hand, and within a few weeks the two
disagree. Nobody can tell which one is wrong, because the table has no memory
of where its numbers came from.

## Approach

Record results as facts and never store the table.

Matches are the only thing written to the database. The standings are
recalculated from them on every read. This removes an entire class of bug: the
table cannot contradict the results, because it has no independent existence.
Correcting a result means removing the fact and recording it again; the
standings follow automatically.

This is the same separation used in analytical systems - immutable events at
the base, derived views on top - applied at a scale where it stays readable.

## User stories

| # | As a... | I want to... | so that... |
|---|---------|--------------|------------|
| US1 | league admin | register a team | it appears in the table from matchday zero |
| US2 | league admin | record a finished match with its score | the result is on record |
| US3 | anyone | see the current standings | I know where each team sits |
| US4 | league admin | remove a wrongly entered result | the table corrects itself |
| US5 | anyone | reload the page and see the same data | the league survives a browser refresh |

## Acceptance criteria

**US1 - Register a team**
- Names are unique; a duplicate is rejected with 409.
- A blank or whitespace-only name is rejected with 422.
- A newly registered team appears in the standings with zeroes, not omitted.

**US2 - Record a match**
- Both teams must already exist; otherwise 404.
- A team cannot play itself; rejected with 422.
- Goals are integers from 0 to 99; negatives are rejected with 422.
- A recorded match is never edited in place.

**US3 - View standings**
- Win = 3 points, draw = 1, loss = 0.
- Columns: position, team, played, won, drawn, lost, goals for, goals against,
  goal difference, points.
- Tie-breakers in order: points, goal difference, goals scored, team name.
- Ordering is deterministic: two teams that are genuinely level always appear
  in the same order, so a refresh never reshuffles them.

**US4 - Remove a result**
- Deleting a match returns 204; deleting a missing one returns 404.
- The standings reflect the removal on the next read, with no manual
  adjustment anywhere.

**US5 - Persistence**
- Data is stored in SQLite through SQLAlchemy.
- The database URL is read from the environment, so Postgres can replace
  SQLite without touching application code.

## Data model

`Team`
- `id` - integer, primary key
- `name` - text, unique, 1-60 characters
- `created_at` - timestamp

`Match` (immutable)
- `id` - integer, primary key
- `home_team_id`, `away_team_id` - foreign keys, must differ
- `home_goals`, `away_goals` - non-negative integers
- `played_at` - timestamp

There is no standings table. That is the design.

## API contract

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness check |
| GET | `/teams` | List teams |
| POST | `/teams` | Register a team (201) |
| GET | `/matches` | List recorded results, newest first |
| POST | `/matches` | Record a result (201) |
| DELETE | `/matches/{id}` | Remove a result (204) |
| GET | `/standings` | Derived league table |

Full contract in `openapi.yaml`.

## Non-goals

Out of scope for this version:
- Authentication, roles, multiple leagues
- Fixtures and scheduling (only played matches are recorded)
- Configurable points systems or tie-break rules
- Head-to-head tie-breakers
- Live updates between browsers (a refresh is required)
- Deployment - that is Module 3

## Architecture notes

The league rules live in `backend/app/standings.py` as a pure function. It
imports nothing from FastAPI or SQLAlchemy, takes plain data and returns plain
data. Consequences worth stating explicitly:

- The rules are tested without a database or an HTTP client. `test_standings.py`
  runs in milliseconds and fails for exactly one reason: a rule is wrong.
- Changing the points system or adding a tie-breaker touches one file.
- The endpoint is a thin adapter. It reads rows, converts them, calls the
  function, formats the response. There is no business logic in the web layer.

## Stack

- Frontend: React 19 + Vite
- Backend: FastAPI, managed with uv
- Database: SQLite via SQLAlchemy, URL from environment
- Tests: pytest - unit tests for the rules, integration tests for the API
