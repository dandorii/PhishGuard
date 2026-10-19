import re
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "instance"
    / "phishguard.db"
)


def get_connection():
    """Connect to PostgreSQL only when explicitly enabled; otherwise use SQLite."""
    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"

    if use_postgres:
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError(
                "PHISHGUARD_USE_POSTGRES is enabled, "
                "but DATABASE_URL is not configured."
            )

        return psycopg.connect(
            database_url,
            connect_timeout=10,
            row_factory=dict_row,
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection




def init_db():
    """Create authentication and history tables, applying safe migrations."""
    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"

    with get_connection() as connection:
        # Create the users table first so the ownership foreign key can
        # reference it.
        if use_postgres:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id BIGSERIAL PRIMARY KEY,
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
                    indicator_rules TEXT NOT NULL,
                    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            connection.execute("""
                ALTER TABLE analysis_history
                ADD COLUMN IF NOT EXISTS user_id BIGINT
                REFERENCES users(id) ON DELETE CASCADE
            """)

        else:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

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
                    indicator_rules TEXT NOT NULL,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            columns = connection.execute(
                "PRAGMA table_info(analysis_history)"
            ).fetchall()

            column_names = {column["name"] for column in columns}

            if "user_id" not in column_names:
                connection.execute("""
                    ALTER TABLE analysis_history
                    ADD COLUMN user_id INTEGER
                    REFERENCES users(id) ON DELETE CASCADE
                """)


def save_analysis(analysis_type, result, user_id=None):
    """
    Save analysis metadata and associate it with its owner when provided.
    Submitted URLs and email bodies are never stored.
    """
    if analysis_type not in {"url", "email"}:
        raise ValueError("Unsupported analysis type.")

    if user_id is not None and (
        type(user_id) is not int or user_id < 1
    ):
        raise ValueError("User ID must be a positive integer.")

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
    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"
    placeholder = "%s" if use_postgres else "?"

    insert_sql = f"""
        INSERT INTO analysis_history (
            analysis_type,
            analyzed_at,
            score,
            severity,
            indicator_count,
            indicator_rules,
            user_id
        )
        VALUES (
            {placeholder}, {placeholder}, {placeholder}, {placeholder},
            {placeholder}, {placeholder}, {placeholder}
        )
    """

    values = (
        analysis_type,
        analyzed_at,
        score,
        severity,
        len(rules),
        json.dumps(rules),
        user_id,
    )

    with get_connection() as connection:
        if use_postgres:
            cursor = connection.execute(
                insert_sql + " RETURNING id",
                values,
            )
            return cursor.fetchone()["id"]

        cursor = connection.execute(insert_sql, values)
        return cursor.lastrowid


def get_recent_analyses(user_id, limit=20):
    """Return recent analysis metadata belonging only to one user."""
    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")

    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Limit must be an integer between 1 and 100.")

    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"
    placeholder = "%s" if use_postgres else "?"

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT
                id,
                analysis_type,
                analyzed_at,
                score,
                severity,
                indicator_count,
                indicator_rules
            FROM analysis_history
            WHERE user_id = {placeholder}
            ORDER BY id DESC
            LIMIT {placeholder}
            """,
            (user_id, limit),
        ).fetchall()

    results = []

    for row in rows:
        item = dict(row)
        item["indicator_rules"] = json.loads(item["indicator_rules"])
        results.append(item)

    return results


def delete_analysis(analysis_id, user_id):
    """Delete a history record only if it belongs to the specified user."""
    if type(analysis_id) is not int or analysis_id < 1:
        raise ValueError("Analysis ID must be a positive integer.")

    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")

    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"

    with get_connection() as connection:
        if use_postgres:
            cursor = connection.execute(
                """
                DELETE FROM analysis_history
                WHERE id = %s AND user_id = %s
                RETURNING id
                """,
                (analysis_id, user_id),
            )
            return cursor.fetchone() is not None

        cursor = connection.execute(
            """
            DELETE FROM analysis_history
            WHERE id = ? AND user_id = ?
            """,
            (analysis_id, user_id),
        )
        return cursor.rowcount > 0


def get_dashboard_stats(user_id):
    """Return dashboard statistics and recent activity for one user."""
    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")

    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"
    placeholder = "%s" if use_postgres else "?"

    with get_connection() as connection:
        stats = connection.execute(
            f"""
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
            WHERE user_id = {placeholder}
            """,
            (user_id,),
        ).fetchone()

        rows = connection.execute(
            f"""
            SELECT
                id,
                analysis_type,
                analyzed_at,
                score,
                severity,
                indicator_count,
                indicator_rules
            FROM analysis_history
            WHERE user_id = {placeholder}
            ORDER BY id DESC
            LIMIT 5
            """,
            (user_id,),
        ).fetchall()

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


from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

password_hasher = PasswordHasher()


def normalize_email(email):
    """Normalize and validate an email address."""
    if not isinstance(email, str):
        raise ValueError("A valid email address is required.")

    email = email.strip().lower()

    if (
        len(email) > 254
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        raise ValueError("A valid email address is required.")

    return email


def create_user(email, password):
    """Create an account and store only its Argon2id password hash."""
    email = normalize_email(email)

    if not isinstance(password, str) or not 12 <= len(password) <= 128:
        raise ValueError(
            "Password must be between 12 and 128 characters."
        )

    password_hash = password_hasher.hash(password)
    created_at = datetime.now(timezone.utc).isoformat()
    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"
    placeholder = "%s" if use_postgres else "?"

    with get_connection() as connection:
        try:
            cursor = connection.execute(
                f"""
                INSERT INTO users (email, password_hash, created_at)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                RETURNING id
                """ if use_postgres else """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (email, password_hash, created_at),
            )

            if use_postgres:
                return cursor.fetchone()["id"]

            return cursor.lastrowid

        except (sqlite3.IntegrityError, psycopg.errors.UniqueViolation) as error:
            raise ValueError("An account with that email already exists.") from error


def get_user_by_email(email):
    """Find a user by normalized email without returning the password."""
    email = normalize_email(email)
    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"
    placeholder = "%s" if use_postgres else "?"

    with get_connection() as connection:
        row = connection.execute(
            f"""
            SELECT id, email, password_hash, created_at
            FROM users
            WHERE email = {placeholder}
            """,
            (email,),
        ).fetchone()

    return dict(row) if row else None


def get_user_by_id(user_id):
    """Find an account by its numeric ID."""
    if type(user_id) is not int or user_id < 1:
        return None

    use_postgres = os.getenv("PHISHGUARD_USE_POSTGRES") == "1"
    placeholder = "%s" if use_postgres else "?"

    with get_connection() as connection:
        row = connection.execute(
            f"""
            SELECT id, email, created_at
            FROM users
            WHERE id = {placeholder}
            """,
            (user_id,),
        ).fetchone()

    return dict(row) if row else None


def verify_password(user, password):
    """Verify a password against an account's stored Argon2id hash."""
    if not user or not isinstance(password, str):
        return False

    try:
        return password_hasher.verify(user["password_hash"], password)
    except (VerifyMismatchError, VerificationError, TypeError):
        return False
