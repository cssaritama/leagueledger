# LeagueLedger

A league table that cannot disagree with its own results.

Standings are never stored. Matches are recorded as immutable facts and the
table is recomputed from them on every read, so it has no independent state to
drift out of sync. Remove a result and the table corrects itself.

---

## The design decision

The conventional build stores a `standings` row per team and updates it as
results come in. It works until an update fails halfway, or a result is
corrected, or two writes race. Then the table says one thing, the results say
another, and nothing indicates which is right.

Here the league rules live in one pure function,
[`backend/app/standings.py`](backend/app/standings.py), that takes teams and
matches and returns an ordered table. It imports nothing from the web framework
or the ORM. Two consequences:

- **The rules are testable in isolation.** `tests/test_standings.py` runs with
  no database and no HTTP client. When it fails, a rule is wrong — never the
  plumbing.
- **The table is consistent by construction**, because it is nothing but a
  function of the recorded results.

Full rationale in [`_docs/specs.md`](_docs/specs.md).

## Requirements

- Python 3.11 or later with [uv](https://docs.astral.sh/uv/)
- Node.js 18 or later

## Running it

Backend, on `http://localhost:8000`:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Frontend, on `http://localhost:5173`:

```bash
cd frontend
npm install
npm run dev
```

Interactive API docs are at `http://localhost:8000/docs`.

## Tests

```bash
cd backend
uv run pytest
```

26 tests: 13 covering the league rules, 13 covering the API. Both suites run on
every push via GitHub Actions.

## Configuration

The frontend reads the backend URL from `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

The backend reads `DATABASE_URL`, defaulting to `sqlite:///./leagueledger.db`.
All data access goes through SQLAlchemy, so moving to Postgres is configuration
rather than code:

```bash
export DATABASE_URL="postgresql+psycopg://user:pass@host/leagueledger"
```

## League rules

Win 3 points, draw 1, loss 0. Ties break on goal difference, then goals scored,
then team name alphabetically — so the ordering is deterministic and a refresh
never reshuffles teams that are genuinely level.

## Layout

```
_docs/specs.md              product spec and design rationale
openapi.yaml                API contract
.github/workflows/ci.yml    tests and build on every push
backend/
  app/standings.py          league rules — pure, no I/O
  app/main.py               HTTP adapter around the rules
  app/models.py             ORM models; matches are write-once
  app/db.py                 engine and session, URL from environment
  tests/test_standings.py   rule tests, no database
  tests/test_api.py         endpoint tests, isolated in-memory database
frontend/
  src/api/client.js         the only module that touches the network
  src/components/           table, forms, results list
```

## Author

Carlos Saritama

## License

MIT — see [LICENSE](LICENSE).
