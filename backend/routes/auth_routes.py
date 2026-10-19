"""
VulnSuite — Authentication Routes
====================================
Handles: /register, /login, /logout

VULN_CSRF toggle:
  True  → no CSRF token on state-changing POSTs (login, register)
  False → CSRF token validated
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort)
from db   import get_db
from auth import (hash_password, check_password, login_user, logout_user,
                  current_user, validate_csrf_token)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # ── CSRF check ───────────────────────────────────────────────────────
        if not current_app.config["VULN_CSRF"]:
            # FIXED: validate CSRF token
            token = request.form.get("csrf_token", "")
            if not validate_csrf_token(token):
                abort(403)
        # VULNERABLE (VULN_CSRF=True): no CSRF check at all

        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip()
        password = request.form.get("password", "")

        if not (username and email and password):
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username=? OR email=?", (username, email)
        ).fetchone()
        if existing:
            flash("Username or email already taken.", "error")
            return redirect(url_for("auth.register"))

        db.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?,?,?,?)",
            (username, email, hash_password(password), "user")
        )
        db.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # ── CSRF check ───────────────────────────────────────────────────────
        if not current_app.config["VULN_CSRF"]:
            # FIXED: validate CSRF token
            token = request.form.get("csrf_token", "")
            if not validate_csrf_token(token):
                abort(403)
        # VULNERABLE (VULN_CSRF=True): no CSRF check at all

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db   = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()

        if not user or not check_password(password, user["password"]):
            flash("Invalid credentials.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(f"Welcome back, {user['username']}!", "success")

        next_url = request.args.get("next")
        if next_url:
            if current_app.config["VULN_OPEN_REDIRECT"]:
                # "Security" check: block absolute URLs starting with http
                # STILL VULNERABLE: protocol-relative URLs (//evil.com),
                # backslash-based (\/evil.com), or data: URIs bypass this
                if next_url.lower().startswith("http"):
                    flash("Invalid redirect target.", "error")
                    return redirect(url_for("profile.dashboard"))
                return redirect(next_url)
            else:
                # FIXED: only allow relative, same-site paths.
                from urllib.parse import urlparse
                parsed = urlparse(next_url)
                if not parsed.netloc and not parsed.scheme and next_url.startswith("/"):
                    return redirect(next_url)
                # else: silently ignore an off-site target
        return redirect(url_for("profile.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
