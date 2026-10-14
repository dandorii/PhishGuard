import pytest

from app import app
from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        db,
        "DB_PATH",
        tmp_path / "instance" / "test.db",
    )
    db.init_db()

    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_history_api_returns_empty_list(client):
    response = client.get("/api/history")

    assert response.status_code == 200
    assert response.get_json() == []


def test_history_api_returns_saved_analysis(client):
    db.save_analysis(
        "url",
        {
            "score": 15,
            "severity": "Low",
            "indicators": [
                {"rule": "plain_http", "points": 15}
            ],
        },
    )

    response = client.get("/api/history")
    history = response.get_json()

    assert response.status_code == 200
    assert len(history) == 1
    assert history[0]["analysis_type"] == "url"
    assert history[0]["score"] == 15


def test_delete_history_api(client):
    record_id = db.save_analysis(
        "email",
        {
            "score": 30,
            "severity": "Medium",
            "indicators": [
                {"rule": "credential_request", "points": 30}
            ],
        },
    )

    response = client.delete(
        f"/api/history/{record_id}"
    )

    assert response.status_code == 200
    assert db.get_recent_analyses() == []


def test_delete_missing_history_returns_404(client):
    response = client.delete("/api/history/999")

    assert response.status_code == 404
