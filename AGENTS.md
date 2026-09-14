# AGENTS.md

Working notes and conventions for this repository.

## Context

LeagueLedger records football results and derives a league table from them.
`_docs/specs.md` is the source of truth for behaviour. `openapi.yaml` is the
source of truth for the API surface.

## The one rule that matters

**Standings are never stored.** There is no standings table, no cached table,
no counter incremented on write. `GET /standings` recomputes from the recorded
matches every time. If a change would introduce stored aggregates, stop and
raise it rather than implementing it.

## Layout

- `backend/app/standings.py` - the league rules. Pure functions only. This file
  must never import FastAPI, SQLAlchemy, or anything that does I/O.
- `backend/app/main.py` - HTTP adapter. Reads rows, calls the rules, formats the
  response. No business logic here.
- `backend/app/models.py` - ORM models. `Match` is written once and never updated.
- `frontend/src/api/client.js` - the only module allowed to call `fetch`.

## Rules

1. New behaviour goes in the spec before it goes in the code.
2. Write the test before the implementation.
3. No hardcoded URLs or credentials. Use `VITE_API_BASE_URL` and `DATABASE_URL`.
4. No component calls `fetch` directly; everything goes through `api`.
5. Data access goes through SQLAlchemy. No raw SQL, no SQLite-specific code
   outside `app/db.py`.
6. Tests use an in-memory database and never touch `leagueledger.db`.
7. `openapi.yaml` is generated from the app, not hand-edited.

## Commands

```bash
cd backend  && uv run uvicorn app.main:app --reload   # backend
cd frontend && npm run dev                            # frontend
cd backend  && uv run pytest                          # tests
```

## Definition of done

- `uv run pytest` green
- `npm run build` clean
- Manual check: add two teams, record a result, delete it, confirm the table
  returns to zero without any manual adjustment
