# Engineering decisions

## 1. Matches are facts; standings are derived

The database stores teams and played matches, but not the standings table.
`GET /standings` derives the current table from those facts.

Why:

- there is only one source of truth;
- deleting a match automatically removes its effect;
- a partial write cannot leave standings out of sync with results;
- league rules can be tested without HTTP or a database.

Trade-off: standings are recomputed on reads. That is the correct trade-off at
the current scale. If read volume grows substantially, a derived cache or
materialized read model can be introduced without changing the source of truth.

## 2. Monolith before microservices

The current domain does not justify distributed services. FastAPI, the domain
engine and persistence layer stay in one backend deployment. This keeps the
system easy to understand and operate while preserving clear internal
boundaries.

## 3. SQLite for zero-friction development, PostgreSQL for deployed environments

SQLite makes first-run development easy. SQLAlchemy keeps database access
portable, while PostgreSQL is exercised through CI integration tests and the
containerized environment.

## 4. Liveness and readiness are different

`/health` proves the process is alive. `/ready` verifies the database is
reachable. Kubernetes uses them for different decisions: restart an unhealthy
process, but only route traffic to a ready instance.

## 5. Local Kubernetes is demonstrative, not disguised as production

The `kind` manifests demonstrate orchestration, replicas, probes, secrets and
persistent storage. The repository explicitly documents that production should
use managed PostgreSQL and production-grade persistent storage.
