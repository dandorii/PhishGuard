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
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as test_client:
        yield test_client


def create_test_user(email, password="TestPassword123!"):
    return db.create_user(email, password)


def login_as(client, user_id):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_anonymous_user_cannot_access_history_api(client):
    response = client.get("/api/history")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required."


def test_history_api_returns_only_the_current_users_records(client):
    owner_id = create_test_user("owner@example.com")
    other_user_id = create_test_user("other@example.com")

    db.save_analysis(
        "url",
        {
            "score": 15,
            "severity": "Low",
            "indicators": [{"rule": "plain_http", "points": 15}],
        },
        user_id=owner_id,
    )

    db.save_analysis(
        "email",
        {
            "score": 70,
            "severity": "High",
            "indicators": [{"rule": "credential_request", "points": 70}],
        },
        user_id=other_user_id,
    )

    login_as(client, owner_id)
    response = client.get("/api/history")

    assert response.status_code == 200

    history = response.get_json()
    assert len(history) == 1
    assert history[0]["analysis_type"] == "url"
    assert history[0]["score"] == 15


def test_anonymous_user_cannot_delete_history(client):
    response = client.delete("/api/history/1")

    assert response.status_code == 401


def test_user_can_delete_own_history(client):
    user_id = create_test_user("delete@example.com")

    record_id = db.save_analysis(
        "email",
        {
            "score": 30,
            "severity": "Medium",
            "indicators": [
                {"rule": "credential_request", "points": 30}
            ],
        },
        user_id=user_id,
    )

    login_as(client, user_id)
    response = client.delete(f"/api/history/{record_id}")

    assert response.status_code == 200
    assert db.get_recent_analyses(user_id) == []


def test_user_cannot_delete_another_users_history(client):
    owner_id = create_test_user("record-owner@example.com")
    other_user_id = create_test_user("record-other@example.com")

    record_id = db.save_analysis(
        "url",
        {
            "score": 20,
            "severity": "Low",
            "indicators": [],
        },
        user_id=owner_id,
    )

    login_as(client, other_user_id)
    response = client.delete(f"/api/history/{record_id}")

    assert response.status_code == 404
    assert len(db.get_recent_analyses(owner_id)) == 1


def test_delete_missing_history_returns_404_for_authenticated_user(client):
    user_id = create_test_user("missing@example.com")
    login_as(client, user_id)

    response = client.delete("/api/history/999")

    assert response.status_code == 404

def test_anonymous_user_is_redirected_from_history_page(client):
    response = client.get("/history")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]