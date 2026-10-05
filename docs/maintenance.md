# Maintenance

## Routine checks

- Keep the default branch green in GitHub Actions.
- Review Dependabot updates monthly rather than merging them blindly.
- Run `make test` before each release.
- Run the Docker smoke test whenever container or networking configuration changes.
- Run the local `kind` deployment after changes to Kubernetes manifests.

## Release process

1. Update `CHANGELOG.md`.
2. Confirm backend tests and frontend checks pass.
3. Confirm the PostgreSQL integration job passes in CI.
4. Build the complete Docker Compose stack and run `./scripts/smoke-test.sh`.
5. Tag the release using semantic versioning.

## Database evolution

The current schema is intentionally small and bootstrapped with SQLAlchemy
`create_all`. Before the first schema-changing production release, introduce a
migration tool such as Alembic and stop treating automatic schema creation as a
migration strategy.

## Kubernetes evolution

The included manifests target local `kind`. If the project moves to a hosted
environment:

- use managed PostgreSQL;
- use the platform's secret manager;
- use a production storage class;
- publish versioned container images to a registry;
- add ingress/TLS and environment-specific configuration;
- add observability based on actual operating requirements.
