# Demo guide

A short demo should take about three minutes.

## 1. Start from the product idea

Explain the invariant first:

> Matches are facts. Standings are derived.

The project avoids keeping a second mutable copy of the league table.

## 2. Show the application

Create two teams, record a result and point out that the standings update from
that result.

## 3. Demonstrate the invariant

Delete the match. The table immediately returns both teams to zero without a
manual standings update.

## 4. Show the implementation boundary

Open `backend/app/standings.py`. The league rules are pure Python and independent
from FastAPI and SQLAlchemy.

Then show `backend/tests/test_standings.py` to demonstrate that the rules are
verified without infrastructure.

## 5. Show delivery quality

Highlight:

- PostgreSQL integration coverage in CI;
- Docker Compose for a complete local stack;
- `/health` and `/ready` probes;
- Kubernetes manifests and the `kind` deployment script;
- architecture and engineering decision documentation.

## 6. Close with the roadmap

Explain that the next product layer would be seasons, competitions and richer
analytics, while keeping recorded match facts as the source of truth.
