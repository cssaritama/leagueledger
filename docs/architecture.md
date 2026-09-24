# LeagueLedger Architecture

## Current Architecture

React frontend communicates with a FastAPI backend.

The backend exposes REST endpoints and uses SQLAlchemy as the persistence layer.

## Design Decision

Standings are derived from match records instead of being stored independently.

This keeps competition data consistent and auditable.

## Future Direction

The architecture is prepared for PostgreSQL, Docker, Kubernetes and automated deployment.
