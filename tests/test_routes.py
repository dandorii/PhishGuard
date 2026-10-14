import pytest

from app import app
from database import db


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    """Keep route tests from writing into the app's real database."""
    monkeypatch.setattr(
        db,
        "DB_PATH",
        tmp_path / "instance" / "test.db",
    )
    db.init_db()


def test_homepage_loads():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"PhishGuard" in response.data


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["application"] == "PhishGuard"


def test_url_analysis_api_returns_results():
    client = app.test_client()

    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["score"] == 0
    assert data["severity"] == "Low"
    assert data["indicators"] == []


def test_url_analysis_api_detects_plain_http():
    client = app.test_client()

    response = client.post(
        "/api/analyze/url",
        json={"url": "http://example.com"},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["score"] == 15
    assert any(
        item["rule"] == "plain_http"
        for item in data["indicators"]
    )


def test_url_analysis_api_rejects_invalid_url():
    client = app.test_client()

    response = client.post(
        "/api/analyze/url",
        json={"url": "ftp://example.com"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_url_analysis_api_rejects_missing_url():
    client = app.test_client()

    response = client.post(
        "/api/analyze/url",
        json={},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_url_analysis_api_rejects_non_json_request():
    client = app.test_client()

    response = client.post(
        "/api/analyze/url",
        data="not json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_email_analysis_api_returns_results():
    client = app.test_client()

    response = client.post(
        "/api/analyze/email",
        json={"email": "Hello, the meeting is tomorrow."},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["score"] == 0
    assert data["severity"] == "Low"
    assert data["indicators"] == []


def test_email_analysis_api_detects_credential_request():
    client = app.test_client()

    response = client.post(
        "/api/analyze/email",
        json={
            "email": (
                "Urgent action required. "
                "Please enter your password."
            )
        },
    )

    assert response.status_code == 200

    data = response.get_json()
    rules = [item["rule"] for item in data["indicators"]]

    assert "urgency_language" in rules
    assert "credential_request" in rules


def test_email_analysis_api_rejects_empty_content():
    client = app.test_client()

    response = client.post(
        "/api/analyze/email",
        json={"email": ""},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_email_analysis_api_rejects_missing_email():
    client = app.test_client()

    response = client.post(
        "/api/analyze/email",
        json={},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_email_analysis_api_rejects_non_json_request():
    client = app.test_client()

    response = client.post(
        "/api/analyze/email",
        data="not json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
