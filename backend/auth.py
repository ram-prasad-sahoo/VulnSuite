"""
VulnSuite — Authentication helpers
"""

import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for, abort, current_app


# ── Password hashing ────────────────────────────────────────────────────────
# DELIBERATELY WEAK: no salt, raw SHA-256.
# In a real app use bcrypt/argon2id.

def hash_password(plaintext: str) -> str:
    """SHA-256 hex digest — intentionally weak for the lab."""
    return hashlib.sha256(plaintext.encode()).hexdigest()


def check_password(plaintext: str, stored_hash: str) -> bool:
    return hash_password(plaintext) == stored_hash


# ── Session helpers ─────────────────────────────────────────────────────────

def login_user(user_row):
    """Store user info in the Flask session."""
    session.permanent = True
    session["user_id"]   = user_row["id"]
    session["username"]  = user_row["username"]
    session["role"]      = user_row["role"]


def logout_user():
    session.clear()


def current_user():
    return {
        "id":       session.get("user_id"),
        "username": session.get("username"),
        "role":     session.get("role"),
    } if "user_id" in session else None


# ── Decorators ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user():
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Require at least 'support-admin' role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = current_user()
        if not user or user["role"] not in ("support-admin", "super-admin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    """
    Require 'super-admin' role.
    VULNERABLE (when VULN_BAC=True): decorator is NOT applied to sensitive
    routes — the check happens only in the template (client-side).
    FIXED (VULN_BAC=False): this decorator IS enforced server-side.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = current_user()
        if not user or user["role"] != "super-admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── CSRF helpers ────────────────────────────────────────────────────────────

def generate_csrf_token() -> str:
    token = secrets.token_hex(32)
    session["csrf_token"] = token
    return token


def validate_csrf_token(submitted: str) -> bool:
    stored = session.get("csrf_token")
    if not stored or not submitted:
        return False
    return secrets.compare_digest(stored, submitted)
