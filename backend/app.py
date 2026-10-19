"""
VulnSuite — Main Flask Application Entry Point
=================================================
⚠️  EDUCATIONAL USE ONLY — deliberately vulnerable.
    Do NOT deploy outside an isolated lab network.
"""

import os
import logging
from flask import Flask, request, g
from config import Config
from db import get_db, close_db, init_db
from auth import current_user, generate_csrf_token

# ── Blueprint imports ────────────────────────────────────────────────────────
from routes.auth_routes    import auth_bp
from routes.profile_routes import profile_bp
from routes.invoice_routes import invoice_bp
from routes.admin_routes   import admin_bp
from routes.document_routes import document_bp
from routes.page_routes    import page_bp
from routes.webhook_routes import webhook_bp
from routes.extra_routes   import extra_bp
from routes.upload_routes  import upload_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # ── Register blueprints ──────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(page_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(extra_bp)
    app.register_blueprint(upload_bp)

    # ── DB lifecycle ─────────────────────────────────────────────────────────
    app.teardown_appcontext(close_db)
    init_db(app)

    # ── Request logging ──────────────────────────────────────────────────────
    # Simple request logger — sanitized. The RCE vector is now via file upload
    # (upload_routes.py), NOT via log poisoning. See upload_routes.py for the
    # full RCE chain documentation.
    @app.before_request
    def log_request():
        log_dir = os.path.join(app.root_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "access.log")

        user_agent = request.headers.get("User-Agent", "")
        path       = request.path

        # Sanitize: strip newlines and non-printable chars
        safe_ua   = "".join(c for c in user_agent if c.isprintable() and c not in "\r\n")
        safe_path = "".join(c for c in path      if c.isprintable() and c not in "\r\n")
        line = f"{safe_path} | UA: {safe_ua}\n"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)

    # ── Template globals ─────────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        ctx = {
            "current_user": current_user(),
            "config":       app.config,
        }
        # Provide CSRF token in every template when CSRF protection is ON
        if not app.config["VULN_CSRF"]:
            ctx["csrf_token"] = generate_csrf_token()
        return ctx

    # ── Index redirect ───────────────────────────────────────────────────────
    from flask import redirect, url_for

    @app.route("/")
    def index():
        user = current_user()
        if user:
            return redirect(url_for("profile.dashboard"))
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    # threaded=True matters for the Bonus Track race-condition challenge
    # (/invoice/<id>/redeem): a single-threaded dev server would serialize
    # concurrent requests itself and mask the bug. SQLite's own locking
    # still means requests can block each other briefly, but with
    # threaded=True + the deliberate time.sleep() in the vulnerable branch,
    # the check-then-act window is wide enough that firing ~15-20
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"], threaded=True)
