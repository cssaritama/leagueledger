# Changelog

## [1.0.2] - 2026-10-05

### Fixed

- Stabilized backend linting for the test bootstrap import order.
- Removed legacy deployment files from the portfolio release.
- Kept `compose.yaml` as the single Docker Compose definition.
- Cleaned local caches and generated artifacts from the repository package.


## 1.0.0

Portfolio release.

- Added PostgreSQL support and integration testing.
- Added separate liveness and readiness endpoints.
- Added production-style backend and frontend containers.
- Added a complete Docker Compose environment.
- Added local Kubernetes deployment with kind, probes, replicas and persistent database storage.
- Expanded CI to validate backend, PostgreSQL integration, frontend and container builds.
- Added architecture, engineering decision and deployment documentation.
