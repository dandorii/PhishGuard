import re

import pytest

from app import app
from database import db


VALID_PASSWORD = "StrongTestPass123!"
CSRF_PATTERN = re.compile(rb'name="csrf_token" value="([^"]+)"')


def _build_client(tmp_path, monkeypatch, csrf_enabled):
    monkeypatch.setattr(
        db,
        "DB_PATH",
        tmp_path / "instance" / "test.db",
    )
    db.init_db()

    app.config["TESTING"] = True
    previous_csrf = app.config.get("WTF_CSRF_ENABLED", True)
    app.config["WTF_CSRF_ENABLED"] = csrf_enabled

    return previous_csrf


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Test client with CSRF disabled, for checking page markup and routes."""
    previous_csrf = _build_client(tmp_path, monkeypatch, csrf_enabled=False)

    try:
        with app.test_client() as test_client:
            yield test_client
    finally:
        app.config["WTF_CSRF_ENABLED"] = previous_csrf


@pytest.fixture
def csrf_client(tmp_path, monkeypatch):
    """Test client with the real CSRF protection turned on."""
    previous_csrf = _build_client(tmp_path, monkeypatch, csrf_enabled=True)

    try:
        with app.test_client() as test_client:
            yield test_client
    finally:
        app.config["WTF_CSRF_ENABLED"] = previous_csrf


# ---------- Page markup and navigation ----------

def test_login_page_links_to_register(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b'href="/register"' in response.data


def test_register_page_links_to_login(client):
    response = client.get("/register")

    assert response.status_code == 200
    assert b'href="/login"' in response.data


def test_login_fields_have_visible_labels(client):
    html = client.get("/login").data

    assert b'<label for="email">' in html
    assert b'<label for="password">' in html


def test_register_fields_have_visible_labels(client):
    html = client.get("/register").data

    assert b'<label for="email">' in html
    assert b'<label for="password">' in html
    assert b'<label for="confirm_password">' in html


def test_login_has_one_password_toggle(client):
    html = client.get("/login").data

    assert html.count(b"data-password-toggle") == 1
    assert b'aria-controls="password"' in html


def test_register_has_independent_password_toggles(client):
    html = client.get("/register").data

    assert html.count(b"data-password-toggle") == 2
    assert b'aria-controls="password"' in html
    assert b'aria-controls="confirm_password"' in html


def test_register_hint_matches_backend_rules(client):
    html = client.get("/register").data

    assert b"Must be 12 to 128 characters." in html
    assert b'minlength="12"' in html
    assert b'maxlength="128"' in html


def test_login_preserves_next_parameter_in_form(client):
    response = client.get("/login?next=/methodology")

    assert response.status_code == 200
    assert b'name="next"' in response.data
    assert b'value="/methodology"' in response.data


def test_auth_script_is_served(client):
    page = client.get("/login").data
    assert b"js/auth.js" in page

    script = client.get("/static/js/auth.js")
    assert script.status_code == 200


def test_danger_color_token_is_defined():
    css_path = (
        app.root_path + "/static/css/style.css"
    )
    with open(css_path, encoding="utf-8") as stylesheet:
        css = stylesheet.read()

    assert "--danger: #f87171;" in css


# ---------- Backend password rule (must match the hint) ----------

def test_register_rejects_password_shorter_than_12(client):
    response = client.post(
        "/register",
        data={
            "email": "student@example.com",
            "password": "Short1!abcd",
            "confirm_password": "Short1!abcd",
        },
    )

    assert response.status_code == 400
    assert db.get_user_by_email("student@example.com") is None


def test_register_rejects_password_longer_than_128(client):
    too_long = "A" * 129

    response = client.post(
        "/register",
        data={
            "email": "student@example.com",
            "password": too_long,
            "confirm_password": too_long,
        },
    )

    assert response.status_code == 400
    assert db.get_user_by_email("student@example.com") is None


def test_register_accepts_password_of_exactly_12(client):
    twelve = "Abcdefghij1!"

    response = client.post(
        "/register",
        data={
            "email": "student@example.com",
            "password": twelve,
            "confirm_password": twelve,
        },
    )

    assert response.status_code == 302
    assert db.get_user_by_email("student@example.com") is not None


# ---------- CSRF protection ----------

def test_login_csrf_token_is_present_in_form(csrf_client):
    html = csrf_client.get("/login").data

    assert CSRF_PATTERN.search(html) is not None


def test_register_csrf_token_is_present_in_form(csrf_client):
    html = csrf_client.get("/register").data

    assert CSRF_PATTERN.search(html) is not None


def test_register_post_without_csrf_token_is_rejected(csrf_client):
    response = csrf_client.post(
        "/register",
        data={
            "email": "student@example.com",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 400
    assert db.get_user_by_email("student@example.com") is None


def test_login_post_without_csrf_token_is_rejected(csrf_client):
    db.create_user("student@example.com", VALID_PASSWORD)

    response = csrf_client.post(
        "/login",
        data={
            "email": "student@example.com",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 400

    with csrf_client.session_transaction() as session:
        assert "user_id" not in session


def test_register_post_with_csrf_token_succeeds(csrf_client):
    page = csrf_client.get("/register").data
    token = CSRF_PATTERN.search(page).group(1).decode()

    response = csrf_client.post(
        "/register",
        data={
            "csrf_token": token,
            "email": "student@example.com",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 302
    assert db.get_user_by_email("student@example.com") is not None


def test_login_post_with_csrf_token_succeeds(csrf_client):
    db.create_user("student@example.com", VALID_PASSWORD)

    page = csrf_client.get("/login").data
    token = CSRF_PATTERN.search(page).group(1).decode()

    response = csrf_client.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "student@example.com",
            "password": VALID_PASSWORD,
        },
    )

    assert response.status_code == 302

    with csrf_client.session_transaction() as session:
        assert "user_id" in session
