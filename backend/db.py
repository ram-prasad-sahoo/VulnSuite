"""
VulnSuite — Database Helpers
"""

import sqlite3
import os
from flask import g, current_app


def get_db():
    """Open a thread-local database connection."""
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES,
                               timeout=10)
        g.db.row_factory = sqlite3.Row
        # Let SQLite queue up concurrent writers instead of failing
        # immediately with "database is locked" — needed now that the
        # app runs threaded=True for the race-condition bonus challenge.
        g.db.execute("PRAGMA busy_timeout = 8000")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create schema if it doesn't already exist."""
    with app.app_context():
        db = get_db()
        schema_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,          -- SHA-256 hex (deliberately weak, no salt)
            role        TEXT NOT NULL DEFAULT 'user',
            bio         TEXT DEFAULT '',
            website     TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL NOT NULL,
            description TEXT NOT NULL,
            status      TEXT DEFAULT 'pending',
            discount_redeemed INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Bonus track: single-use discount codes (race-condition target)
        CREATE TABLE IF NOT EXISTS discount_codes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT UNIQUE NOT NULL,
            percent_off INTEGER NOT NULL,
            max_uses    INTEGER NOT NULL DEFAULT 1,
            uses        INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            token       TEXT UNIQUE NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            action      TEXT NOT NULL,
            detail      TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        """
        db.executescript(schema_sql)
        db.commit()
