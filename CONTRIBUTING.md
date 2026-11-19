# Contributing

1. Create a focused branch from `main`.
2. Update `docs/product-spec.md` when behavior changes.
3. Add or update tests before changing business rules.
4. Run `make test` before opening a pull request.
5. Keep standings derived from match facts; do not introduce a stored standings table.

A change is ready when backend tests pass, frontend lint/build succeeds and the
Docker stack passes `./scripts/smoke-test.sh` when infrastructure is affected.

## How this repository is run

Profile `product`. Data class Public. State Active. Owner Carlos Saritama.
README.md states what is deployed and what is not.

Before starting work, read:

1. `README.md`
2. `docs/product-spec.md`, the behavioral source of truth
3. `docs/standards/PROJECT_STANDARDS.md` and `docs/standards/PROFILE.md`

Then follow links only as far as the change needs. Do not read generated build output
unless the change needs that evidence.

Rules:

- LeagueLedger records football matches as facts and derives standings from them. If scale requires faster reads, use a rebuildable cache while matches stay the source of truth.
- `backend/app/standings.py` holds pure domain rules, with no FastAPI, SQLAlchemy or I/O. `backend/app/main.py` is the HTTP adapter, `backend/app/models.py` the persistence models, and `frontend/src/api/client.js` the only frontend module that calls the network.
- Never hardcode production credentials. Keep `/health` independent from external dependencies and `/ready` representative of database availability.
- Keep Docker Compose reproducible with one command, and do not present local Kubernetes `hostPath` storage as production infrastructure.
- `docs/standards/` is a verified copy of the Systems Studio Engineering Standard. Do not edit it; start specifications, decisions and verification records from `docs/standards/templates/`.
- Work on a focused branch and open a pull request. Keep `main` working.

Verify:

```bash
make test
make up
make smoke
```
