
import sqlite3

import pytest

from database import db


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Give each test its own temporary database."""
    monkeypatch.setattr(
        db,
        "DB_PATH",
        tmp_path / "instance" / "test.db",
    )

    db.init_db()
    return db


def test_database_table_is_created(test_db):
    with test_db.get_connection() as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'analysis_history'
            """
        ).fetchall()

    assert len(rows) == 1


def test_save_and_retrieve_analysis(test_db):
    user_id = test_db.create_user(
        "owner@example.com",
        "TestPassword123!",
    )

    result = {
        "score": 15,
        "severity": "Low",
        "indicators": [
            {"rule": "plain_http", "points": 15}
        ],
    }

    record_id = test_db.save_analysis(
        "url",
        result,
        user_id=user_id,
    )
    history = test_db.get_recent_analyses(user_id)

    assert record_id == 1
    assert len(history) == 1
    assert history[0]["analysis_type"] == "url"
    assert history[0]["score"] == 15
    assert history[0]["indicator_rules"] == ["plain_http"]


def test_email_history_does_not_store_email_body(test_db):
    user_id = test_db.create_user(
        "email@example.com",
        "TestPassword123!",
    )

    result = {
        "score": 30,
        "severity": "Medium",
        "indicators": [
            {"rule": "credential_request", "points": 30}
        ],
    }

    test_db.save_analysis(
        "email",
        result,
        user_id=user_id,
    )

    history = test_db.get_recent_analyses(user_id)

    assert len(history) == 1
    assert history[0]["analysis_type"] == "email"
    assert history[0]["indicator_rules"] == ["credential_request"]
    assert "email_body" not in history[0]


def test_invalid_analysis_type_is_rejected(test_db):
    with pytest.raises(ValueError):
        test_db.save_analysis(
            "unknown",
            {
                "score": 0,
                "severity": "Low",
                "indicators": [],
            },
        )


def test_delete_analysis(test_db):
    user_id = test_db.create_user(
        "delete@example.com",
        "TestPassword123!",
    )

    record_id = test_db.save_analysis(
        "url",
        {
            "score": 0,
            "severity": "Low",
            "indicators": [],
        },
        user_id=user_id,
    )

    assert test_db.delete_analysis(record_id, user_id) is True
    assert test_db.get_recent_analyses(user_id) == []


def test_invalid_history_limit_is_rejected(test_db):
    with pytest.raises(ValueError):
        test_db.get_recent_analyses(0)


def test_database_uses_parameterized_queries(test_db):
    user_id = test_db.create_user(
        "sql-test@example.com",
        "TestPassword123!",
    )

    record_id = test_db.save_analysis(
        "url",
        {
            "score": 0,
            "severity": "Low",
            "indicators": [],
        },
        user_id=user_id,
    )

    # SQL-like input must be rejected.
    with pytest.raises(ValueError):
        test_db.delete_analysis(
            "1; DROP TABLE analysis_history",
            user_id,
        )

    history = test_db.get_recent_analyses(user_id)

    assert len(history) == 1
    assert history[0]["id"] == record_id


def test_create_user_stores_argon2id_hash(test_db):
    user_id = test_db.create_user(
        "Student@Example.com",
        "a-strong-test-password",
    )

    user = test_db.get_user_by_email("student@example.com")

    assert user is not None
    assert user["id"] == user_id
    assert user["email"] == "student@example.com"
    assert user["password_hash"].startswith("$argon2id$")
    assert user["password_hash"] != "a-strong-test-password"


def test_verify_password(test_db):
    test_db.create_user(
        "student@example.com",
        "a-strong-test-password",
    )

    user = test_db.get_user_by_email("student@example.com")

    assert test_db.verify_password(
        user,
        "a-strong-test-password",
    ) is True

    assert test_db.verify_password(
        user,
        "incorrect-password",
    ) is False


def test_get_user_by_id_does_not_return_password_hash(test_db):
    user_id = test_db.create_user(
        "student@example.com",
        "a-strong-test-password",
    )

    user = test_db.get_user_by_id(user_id)

    assert user is not None
    assert user["id"] == user_id
    assert "password_hash" not in user


def test_create_user_rejects_short_password(test_db):
    with pytest.raises(ValueError):
        test_db.create_user(
            "student@example.com",
            "short",
        )


def test_create_user_rejects_duplicate_email(test_db):
    test_db.create_user(
        "student@example.com",
        "a-strong-test-password",
    )

    with pytest.raises(ValueError, match="already exists"):
        test_db.create_user(
            "STUDENT@example.com",
            "another-strong-password",
        )

def test_user_cannot_delete_another_users_analysis(test_db):
    owner_id = test_db.create_user(
        "owner@example.com",
        "OwnerPassword123!",
    )
    other_user_id = test_db.create_user(
        "other@example.com",
        "OtherPassword123!",
    )

    record_id = test_db.save_analysis(
        "url",
        {
            "score": 20,
            "severity": "Low",
            "indicators": [],
        },
        user_id=owner_id,
    )

    # The other user must not be able to delete this record.
    assert test_db.delete_analysis(record_id, other_user_id) is False

    # The owner's record must still exist.
    owner_history = test_db.get_recent_analyses(owner_id)
    assert len(owner_history) == 1
    assert owner_history[0]["id"] == record_id

    # The other user must not see the owner's history.
    assert test_db.get_recent_analyses(other_user_id) == []

def test_dashboard_stats_only_include_the_users_own_analyses(test_db):
    owner_id = test_db.create_user(
        "dashboard-owner@example.com",
        "OwnerPassword123!",
    )
    other_user_id = test_db.create_user(
        "dashboard-other@example.com",
        "OtherPassword123!",
    )

    test_db.save_analysis(
        "url",
        {
            "score": 70,
            "severity": "High",
            "indicators": [{"rule": "suspicious_domain", "points": 70}],
        },
        user_id=owner_id,
    )

    test_db.save_analysis(
        "email",
        {
            "score": 10,
            "severity": "Low",
            "indicators": [{"rule": "plain_http", "points": 10}],
        },
        user_id=other_user_id,
    )

    owner_stats = test_db.get_dashboard_stats(owner_id)
    other_stats = test_db.get_dashboard_stats(other_user_id)

    assert owner_stats["total_scans"] == 1
    assert owner_stats["suspicious_results"] == 1
    assert owner_stats["high_risk_results"] == 1
    assert len(owner_stats["recent_activity"]) == 1
    assert owner_stats["recent_activity"][0]["score"] == 70

    assert other_stats["total_scans"] == 1
    assert other_stats["suspicious_results"] == 0
    assert other_stats["high_risk_results"] == 0
    assert len(other_stats["recent_activity"]) == 1
    assert other_stats["recent_activity"][0]["score"] == 10