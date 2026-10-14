import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "instance"
    / "phishguard.db"
)


def get_connection():
    """Create a SQLite connection and ensure the database folder exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """Create the analysis history table if it doesn't exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT NOT NULL
                    CHECK (analysis_type IN ('url', 'email')),
                analyzed_at TEXT NOT NULL,
                score INTEGER NOT NULL
                    CHECK (score BETWEEN 0 AND 100),
                severity TEXT NOT NULL
                    CHECK (severity IN (
                        'Low', 'Medium', 'High', 'Critical'
                    )),
                indicator_count INTEGER NOT NULL
                    CHECK (indicator_count >= 0),
                indicator_rules TEXT NOT NULL
            )
        """)


def save_analysis(analysis_type, result):
    """
    Save analysis metadata without storing the submitted URL or email body.

    Only indicator rule identifiers are persisted, not submitted content.
    """
    if analysis_type not in {"url", "email"}:
        raise ValueError("Unsupported analysis type.")

    score = result.get("score")
    severity = result.get("severity")
    indicators = result.get("indicators")

    if (
        type(score) is not int
        or not 0 <= score <= 100
        or severity not in {"Low", "Medium", "High", "Critical"}
        or not isinstance(indicators, list)
    ):
        raise ValueError("Invalid analysis result.")

    rules = []

    for indicator in indicators:
        if not isinstance(indicator, dict):
            raise ValueError("Invalid indicator.")

        rule = indicator.get("rule")

        if not isinstance(rule, str) or not rule:
            raise ValueError("Invalid indicator rule.")

        rules.append(rule)

    analyzed_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analysis_history (
                analysis_type,
                analyzed_at,
                score,
                severity,
                indicator_count,
                indicator_rules
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                analysis_type,
                analyzed_at,
                score,
                severity,
                len(rules),
                json.dumps(rules),
            ),
        )

        return cursor.lastrowid


def get_recent_analyses(limit=20):
    """Return recent analysis metadata, newest first."""
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Limit must be an integer between 1 and 100.")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                analysis_type,
                analyzed_at,
                score,
                severity,
                indicator_count,
                indicator_rules
            FROM analysis_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    results = []

    for row in rows:
        item = dict(row)
        item["indicator_rules"] = json.loads(item["indicator_rules"])
        results.append(item)

    return results


def delete_analysis(analysis_id):
    """Delete a history record by its integer ID."""
    if type(analysis_id) is not int or analysis_id < 1:
        raise ValueError("Analysis ID must be a positive integer.")

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM analysis_history WHERE id = ?",
            (analysis_id,),
        )

        return cursor.rowcount > 0


def get_dashboard_stats():
    """Return dashboard statistics and recent analysis metadata."""
    with get_connection() as connection:
        stats = connection.execute("""
            SELECT
                COUNT(*) AS total_scans,
                COALESCE(
                    SUM(CASE WHEN score >= 30 THEN 1 ELSE 0 END),
                    0
                ) AS suspicious_results,
                COALESCE(
                    SUM(CASE WHEN score >= 60 THEN 1 ELSE 0 END),
                    0
                ) AS high_risk_results
            FROM analysis_history
        """).fetchone()

        rows = connection.execute("""
            SELECT
                id,
                analysis_type,
                analyzed_at,
                score,
                severity,
                indicator_count,
                indicator_rules
            FROM analysis_history
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()

    recent_activity = []

    for row in rows:
        item = dict(row)
        item["indicator_rules"] = json.loads(
            item["indicator_rules"]
        )
        recent_activity.append(item)

    return {
        "total_scans": stats["total_scans"],
        "suspicious_results": stats["suspicious_results"],
        "high_risk_results": stats["high_risk_results"],
        "recent_activity": recent_activity,
    }
