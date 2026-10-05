# AGENTS.md

Repository conventions for coding agents and contributors.

## Product rule

LeagueLedger records football matches as facts and derives standings from those
facts. `docs/product-spec.md` is the behavioral source of truth.

**Never introduce a stored standings table or mutable standings counters.**
If scale later requires faster reads, use a rebuildable cache/read model while
preserving matches as the source of truth.

## Boundaries

- `backend/app/standings.py`: pure domain rules; no FastAPI, SQLAlchemy or I/O.
- `backend/app/main.py`: HTTP adapter and persistence orchestration.
- `backend/app/models.py`: persistence models.
- `frontend/src/api/client.js`: the only frontend module that performs network calls.
- `docs/`: architecture, decisions, deployment and API examples.

## Development rules

1. Update the product spec when observable behavior changes.
2. Add or update tests before changing league rules.
3. Never hardcode production credentials.
4. Keep `/health` independent from external dependencies.
5. Keep `/ready` representative of database availability.
6. Keep Docker Compose reproducible with one command.
7. Keep local Kubernetes honest: do not present `hostPath` storage as production infrastructure.

## Verification

```bash
make test
# With Docker available:
make up
make smoke
```
