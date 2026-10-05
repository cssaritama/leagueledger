# Contributing

1. Create a focused branch from `main`.
2. Update `docs/product-spec.md` when behavior changes.
3. Add or update tests before changing business rules.
4. Run `make test` before opening a pull request.
5. Keep standings derived from match facts; do not introduce a stored standings table.

A change is ready when backend tests pass, frontend lint/build succeeds and the
Docker stack passes `./scripts/smoke-test.sh` when infrastructure is affected.
