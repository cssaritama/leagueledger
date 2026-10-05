"""Integration test against the configured PostgreSQL database.

The test is opt-in so the default local test suite stays self-contained.
CI enables it with RUN_POSTGRES_TESTS=1 and a disposable PostgreSQL service.
"""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db import SessionLocal
from app.main import app
from app.models import Match, Team

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_TESTS") != "1",
    reason="PostgreSQL integration test is opt-in",
)


def test_postgres_round_trip():
    suffix = uuid4().hex[:8]
    home_name = f"Northbridge-{suffix}"
    away_name = f"Riverside-{suffix}"

    with TestClient(app) as client:
        home = client.post("/teams", json={"name": home_name})
        away = client.post("/teams", json={"name": away_name})
        assert home.status_code == 201
        assert away.status_code == 201

        match = client.post(
            "/matches",
            json={
                "home_team_id": home.json()["id"],
                "away_team_id": away.json()["id"],
                "home_goals": 2,
                "away_goals": 1,
            },
        )
        assert match.status_code == 201
        assert client.get("/ready").json() == {"status": "ready"}

        table = client.get("/standings").json()
        row = next(item for item in table if item["team"] == home_name)
        assert row["points"] == 3

    with SessionLocal() as db:
        db.execute(delete(Match).where(Match.id == match.json()["id"]))
        db.execute(delete(Team).where(Team.name.in_([home_name, away_name])))
        db.commit()
