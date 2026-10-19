#!/usr/bin/env python3
"""
Shadow Corp — Database Seed Script
====================================
Creates:
  - 5 normal users (alice, bob, carol, dave, eve)
  - 1 support-admin (support_admin)
  - 1 super-admin  (superadmin)
  - Sample invoices and private data for each user

Run inside the container or locally:
    python seed.py
"""

import sqlite3
import hashlib
import os
import sys

DB_PATH = os.environ.get("DATABASE", "/app/LabDatabase.db")


def hash_password(plaintext: str) -> str:
    """SHA-256 (no salt) — matches app.auth.hash_password."""
    return hashlib.sha256(plaintext.encode()).hexdigest()


USERS = [
    # (username, email, password, role, bio)
    ("alice",         "alice@shadowcorp.com",   "Password123!", "user",
     "Hi, I'm Alice. I manage the product roadmap here at Shadow Corp."),
    ("bob",           "bob@shadowcorp.com",     "Password123!", "user",
     "Bob here — lead engineer on the Shadow Platform. Coffee enthusiast."),
    ("carol",         "carol@shadowcorp.com",   "Password123!", "user",
     "Carol — finance analyst. Ask me about Q3 projections."),
    ("dave",          "dave@shadowcorp.com",    "Password123!", "user",
     "David Chen, Head of Sales. Always closing."),
    ("eve",           "eve@shadowcorp.com",     "Password123!", "user",
     "Eve — new here. Still getting set up!"),
    ("support_admin", "support@shadowcorp.com", "Admin@Shadow1", "support-admin",
     "Support admin account. Internal use only."),
    ("superadmin",    "admin@shadowcorp.com",   "Super@Shadow1", "super-admin",
     "Super administrator. Full system access."),
]

INVOICES = [
    # (username, amount, description, status)
    ("alice", 4500.00,  "Q3 Product Strategy Consulting",       "paid"),
    ("alice", 1250.00,  "UX Research Report",                   "pending"),
    ("bob",   9800.00,  "Platform Infrastructure Sprint",        "paid"),
    ("bob",   3300.00,  "Security Audit — October",              "pending"),
    ("carol", 2100.00,  "Financial Modelling — Series B",        "paid"),
    ("carol", 750.00,   "Expense Reimbursement — Q3",           "overdue"),
    ("carol", 5600.00,  "Investor Relations Package",            "paid"),
    ("dave",  8200.00,  "Corporate Sales Contract — Nexus",     "paid"),
    ("dave",  4100.00,  "Demo Environment Setup",                "pending"),
    ("eve",   320.00,   "Onboarding Kit",                        "paid"),
    ("support_admin", 0.00, "Internal account — no billing",    "paid"),
    ("superadmin",    0.00, "Internal account — no billing",    "paid"),
]


def seed(db_path: str):
    print(f"[*] Seeding database: {db_path}")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Create schema
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT UNIQUE NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,
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
    """)
    conn.commit()

    # Clear existing data
    c.execute("DELETE FROM invoices")
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM audit_log")
    c.execute("DELETE FROM discount_codes")
    conn.commit()

    # Insert users
    user_ids = {}
    for username, email, password, role, bio in USERS:
        c.execute(
            "INSERT INTO users (username, email, password, role, bio) VALUES (?,?,?,?,?)",
            (username, email, hash_password(password), role, bio)
        )
        user_ids[username] = c.lastrowid
        print(f"  [+] User: {username:20s} role={role:15s} id={c.lastrowid}")

    conn.commit()

    # Insert invoices
    for username, amount, description, status in INVOICES:
        user_id = user_ids.get(username)
        if user_id:
            c.execute(
                "INSERT INTO invoices (user_id, amount, description, status) VALUES (?,?,?,?)",
                (user_id, amount, description, status)
            )
    conn.commit()

    # Bonus track: a single-use welcome discount code (race-condition target)
    c.execute(
        "INSERT INTO discount_codes (code, percent_off, max_uses, uses) VALUES (?,?,?,0)",
        ("WELCOME10", 10, 1)
    )
    conn.commit()

    # Seed audit log with some history
    c.execute(
        "INSERT INTO audit_log (user_id, action, detail) VALUES (?,?,?)",
        (user_ids["superadmin"], "system_init", "Database seeded for lab environment")
    )
    c.execute(
        "INSERT INTO audit_log (user_id, action, detail) VALUES (?,?,?)",
        (user_ids["support_admin"], "login", "Initial support-admin login")
    )
    conn.commit()
    conn.close()

    print()
    print("=" * 55)
    print("  Seed complete! Credentials:")
    print("=" * 55)
    for username, email, password, role, _ in USERS:
        print(f"  {username:20s} / {password:20s}  [{role}]")
    print("=" * 55)


if __name__ == "__main__":
    seed(DB_PATH)
