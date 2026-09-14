"""Tests for the HTTP layer.

Each test runs against its own in-memory database, so tests cannot contaminate
one another and none of them touch the development database on disk.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def add_team(client, name: str) -> int:
    return client.post("/teams", json={"name": name}).json()["id"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_league_starts_empty(client):
    assert client.get("/teams").json() == []
    assert client.get("/matches").json() == []
    assert client.get("/standings").json() == []


def test_create_team(client):
    r = client.post("/teams", json={"name": "Ajax"})
    assert r.status_code == 201
    assert r.json()["name"] == "Ajax"


def test_duplicate_team_is_rejected(client):
    client.post("/teams", json={"name": "Ajax"})
    r = client.post("/teams", json={"name": "Ajax"})
    assert r.status_code == 409


def test_blank_team_name_is_rejected(client):
    assert client.post("/teams", json={"name": "   "}).status_code == 422
    assert client.post("/teams", json={"name": ""}).status_code == 422


def test_record_a_match(client):
    home = add_team(client, "Ajax")
    away = add_team(client, "Benfica")

    r = client.post(
        "/matches",
        json={
            "home_team_id": home,
            "away_team_id": away,
            "home_goals": 2,
            "away_goals": 1,
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["home_team"] == "Ajax"
    assert body["away_team"] == "Benfica"


def test_a_team_cannot_play_itself(client):
    team = add_team(client, "Ajax")
    r = client.post(
        "/matches",
        json={
            "home_team_id": team,
            "away_team_id": team,
            "home_goals": 1,
            "away_goals": 0,
        },
    )
    assert r.status_code == 422


def test_match_with_unknown_team_returns_404(client):
    team = add_team(client, "Ajax")
    r = client.post(
        "/matches",
        json={
            "home_team_id": team,
            "away_team_id": 999,
            "home_goals": 1,
            "away_goals": 0,
        },
    )
    assert r.status_code == 404


def test_negative_goals_are_rejected(client):
    home = add_team(client, "Ajax")
    away = add_team(client, "Benfica")
    r = client.post(
        "/matches",
        json={
            "home_team_id": home,
            "away_team_id": away,
            "home_goals": -1,
            "away_goals": 0,
        },
    )
    assert r.status_code == 422


def test_standings_reflect_recorded_matches(client):
    home = add_team(client, "Ajax")
    away = add_team(client, "Benfica")
    client.post(
        "/matches",
        json={
            "home_team_id": home,
            "away_team_id": away,
            "home_goals": 3,
            "away_goals": 0,
        },
    )

    table = client.get("/standings").json()
    assert table[0]["team"] == "Ajax"
    assert table[0]["position"] == 1
    assert table[0]["points"] == 3
    assert table[0]["goal_difference"] == 3
    assert table[1]["team"] == "Benfica"
    assert table[1]["points"] == 0


def test_deleting_a_match_updates_the_table(client):
    home = add_team(client, "Ajax")
    away = add_team(client, "Benfica")
    match_id = client.post(
        "/matches",
        json={
            "home_team_id": home,
            "away_team_id": away,
            "home_goals": 3,
            "away_goals": 0,
        },
    ).json()["id"]

    assert client.get("/standings").json()[0]["points"] == 3

    assert client.delete(f"/matches/{match_id}").status_code == 204

    # The table is derived, so removing the fact removes its effect.
    table = client.get("/standings").json()
    assert all(s["points"] == 0 and s["played"] == 0 for s in table)


def test_deleting_a_missing_match_returns_404(client):
    assert client.delete("/matches/999").status_code == 404


def test_standings_position_is_one_based_and_contiguous(client):
    for name in ("Ajax", "Benfica", "Celtic"):
        add_team(client, name)
    table = client.get("/standings").json()
    assert [s["position"] for s in table] == [1, 2, 3]
