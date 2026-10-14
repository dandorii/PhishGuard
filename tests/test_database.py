
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
    result = {
        "score": 15,
        "severity": "Low",
        "indicators": [
            {"rule": "plain_http", "points": 15}
        ],
    }

    record_id = test_db.save_analysis("url", result)
    history = test_db.get_recent_analyses()

    assert record_id == 1
    assert len(history) == 1
    assert history[0]["analysis_type"] == "url"
    assert history[0]["score"] == 15
    assert history[0]["indicator_rules"] == ["plain_http"]


def test_email_history_does_not_store_email_body(test_db):
    result = {
        "score": 30,
        "severity": "Medium",
        "indicators": [
            {"rule": "credential_request", "points": 30}
        ],
    }

    test_db.save_analysis("email", result)
    history = test_db.get_recent_analyses()

    assert history[0]["analysis_type"] == "email"
    assert "email body" not in str(history).lower()
    assert history[0]["indicator_rules"] == ["credential_request"]


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
    record_id = test_db.save_analysis(
        "url",
        {
            "score": 0,
            "severity": "Low",
            "indicators": [],
        },
    )

    assert test_db.delete_analysis(record_id) is True
    assert test_db.get_recent_analyses() == []
    assert test_db.delete_analysis(record_id) is False


def test_invalid_history_limit_is_rejected(test_db):
    with pytest.raises(ValueError):
        test_db.get_recent_analyses(0)


def test_database_uses_parameterized_queries(test_db):
    record_id = test_db.save_analysis(
        "url",
        {
            "score": 0,
            "severity": "Low",
            "indicators": [],
        },
    )

    # A string containing SQL-like text must not execute as SQL.
    with pytest.raises(ValueError):
        test_db.delete_analysis(
            "1; DROP TABLE analysis_history"
        )

    assert test_db.get_recent_analyses()[0]["id"] == record_id
