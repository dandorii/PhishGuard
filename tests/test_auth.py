
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

    # These tests cover route behavior, not CSRF token validation.
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as test_client:
        yield test_client


def test_register_page_loads(client):
    response = client.get("/register")

    assert response.status_code == 200
    assert b"Create your account" in response.data


def test_register_creates_account_and_signs_user_in(client):
    response = client.post(
        "/register",
        data={
            "email": "student@example.com",
            "password": "StrongTestPass123!",
            "confirm_password": "StrongTestPass123!",
        },
    )

    assert response.status_code == 302
    user = db.get_user_by_email("student@example.com")
    assert user is not None

    with client.session_transaction() as session:
        assert session["user_id"] == user["id"]


def test_register_rejects_mismatched_passwords(client):
    response = client.post(
        "/register",
        data={
            "email": "student@example.com",
            "password": "StrongTestPass123!",
            "confirm_password": "DifferentPass123!",
        },
    )

    assert response.status_code == 400
    assert db.get_user_by_email("student@example.com") is None


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_login_accepts_valid_credentials(client):
    db.create_user("student@example.com", "StrongTestPass123!")

    response = client.post(
        "/login",
        data={
            "email": "student@example.com",
            "password": "StrongTestPass123!",
        },
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "user_id" in session


def test_login_rejects_invalid_password(client):
    db.create_user("student@example.com", "StrongTestPass123!")

    response = client.post(
        "/login",
        data={
            "email": "student@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_logout_clears_session(client):
    with client.session_transaction() as session:
        session["user_id"] = 1

    response = client.post("/logout")

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "user_id" not in session

def test_login_allows_safe_local_redirect(client):
    db.create_user("student@example.com", "StrongTestPass123!")

    response = client.post(
        "/login?next=/methodology",
        data={
            "email": "student@example.com",
            "password": "StrongTestPass123!",
        },
    )

    assert response.status_code == 302
    assert response.location == "/methodology"


def test_login_rejects_external_redirect(client):
    db.create_user("student@example.com", "StrongTestPass123!")

    response = client.post(
        "/login?next=https://evil.example",
        data={
            "email": "student@example.com",
            "password": "StrongTestPass123!",
        },
    )

    assert response.status_code == 302
    assert response.location == "/"