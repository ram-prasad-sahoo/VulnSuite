"""
VulnSuite — Profile Routes
=============================
Handles: /dashboard, /profile/<username>, /profile/edit

VULN_XSS toggle:
  True  → bio AND website rendered with |safe (raw HTML, allows stored XSS)
  False → both HTML-escaped before render

The `website` field is the harder of the two: it's rendered inside an
`<a href="...">` attribute rather than as page body text. A WAF_ENABLED
content filter (waf.py) blocks a plain `javascript:` URI, a base64-wrapped
one, and a single-layer URL-encoded one — but it never decodes HTML
character references. Entity-encoding (decimal or hex) part or all of the
word "javascript" bypasses the filter untouched, and the browser's own
HTML attribute-value parser decodes those entities back into a real
`javascript:` URI the moment the link renders — the classic, genuinely
working version of this bypass (as opposed to entity-encoding a whole
`<script>` tag in body text, which looks similar but does NOT execute,
since HTML entity decoding of body text never re-triggers tag parsing).

VULN_CSRF toggle:
  True  → /profile/edit POST has no CSRF token
  False → CSRF token validated
"""

import html
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort)
from db   import get_db
from auth import login_required, current_user, validate_csrf_token
from waf  import is_blocked

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    db   = get_db()
    me   = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    invoices = db.execute(
        "SELECT * FROM invoices WHERE user_id=? ORDER BY id DESC LIMIT 5",
        (user["id"],)
    ).fetchall()
    return render_template("profile/dashboard.html", me=me, invoices=invoices)


@profile_bp.route("/profile/<username>")
def view_profile(username):
    db   = get_db()
    user = db.execute(
        "SELECT id, username, bio, website, role, created_at FROM users WHERE username=?",
        (username,)
    ).fetchone()
    if not user:
        abort(404)

    # ── XSS toggle ───────────────────────────────────────────────────────────
    if current_app.config["VULN_XSS"]:
        # VULNERABLE: bio/website passed to template with |safe — raw HTML injected
        bio_content     = user["bio"] or ""
        website_content = user["website"] or ""
    else:
        # FIXED: escape all HTML entities before rendering
        bio_content     = html.escape(user["bio"] or "")
        website_content = html.escape(user["website"] or "")

    return render_template("profile/view_profile.html",
                           profile_user=user,
                           bio_content=bio_content,
                           website_content=website_content,
                           vuln_xss=current_app.config["VULN_XSS"])


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = current_user()
    db   = get_db()

    if request.method == "POST":
        # ── CSRF check ───────────────────────────────────────────────────────
        if not current_app.config["VULN_CSRF"]:
            # FIXED: validate CSRF token
            token = request.form.get("csrf_token", "")
            if not validate_csrf_token(token):
                abort(403)
        # VULNERABLE (VULN_CSRF=True): no token check, any cross-site POST works

        bio     = request.form.get("bio",     "")
        website = request.form.get("website", "").strip()
        email   = request.form.get("email",   "").strip()

        # ── Content filter (waf.py) ──────────────────────────────────────────
        # Only meaningful while VULN_XSS is also on — see waf.py for exactly
        # what it catches and, more importantly, what it doesn't. Applied to
        # both fields; the bio field is the "easy" demonstration (plain
        # payload / base64 / URL-encoding all blocked, nothing bypasses it
        # from this field alone), the website field is where the entity-
        # encoding bypass actually fires, because it renders inside an href
        # attribute instead of page body text.
        field_error = None
        if current_app.config["VULN_XSS"] and current_app.config["WAF_ENABLED"]:
            if is_blocked(bio):
                field_error = ("That bio couldn't be saved — it contains content "
                               "that isn't allowed. Please remove any script-like "
                               "text and try again.")
            elif is_blocked(website):
                field_error = ("That website link couldn't be saved — it contains "
                               "content that isn't allowed. Please use a plain "
                               "http(s) URL.")

        if field_error:
            me = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
            me = dict(me)
            me["bio"], me["website"] = bio, website  # redisplay exactly what they typed
            return render_template("profile/edit_profile.html", me=me, bio_error=field_error)

        # ── VULNERABLE: bio/website stored raw — no sanitisation ─────────────
        # FIXED would be: html.escape() before storing, OR escape on output
        # (this app does the latter — see view_profile() above).
        db.execute(
            "UPDATE users SET bio=?, website=?, email=? WHERE id=?",
            (bio, website, email, user["id"])
        )
        db.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile.view_profile", username=user["username"]))

    me = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    return render_template("profile/edit_profile.html", me=me)


@profile_bp.route("/users")
@login_required
def user_list():
    """Public user directory (links to profiles)."""
    db    = get_db()
    users = db.execute(
        "SELECT id, username, role, created_at FROM users ORDER BY id"
    ).fetchall()
    return render_template("profile/user_list.html", users=users)
