"""
Shadow Corp — Admin Routes
===========================
Handles: /admin (dashboard), /admin/users, /admin/promote-user,
         /admin/change-email, /admin/settings

VULN_BAC toggle:
  True  → /admin/settings/promote-user is reachable by any admin role
           (role check only in template, not server-side)
  False → super_admin_required decorator enforced on sensitive routes

VULN_CSRF toggle: same as elsewhere — POST endpoints skip token check when True

VULN_JWT toggle:
  True  → admin JWT passed to internal service without signature verification
  False → JWT signature verified before trusting claims
"""

import json
import base64
import hmac
import hashlib
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort, session)
from db   import get_db
from auth import (login_required, admin_required, super_admin_required,
                  current_user, validate_csrf_token)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Admin Dashboard ──────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    db    = get_db()
    users = db.execute("SELECT * FROM users ORDER BY id").fetchall()
    total_invoices = db.execute("SELECT COUNT(*) as c FROM invoices").fetchone()["c"]
    audit = db.execute(
        "SELECT * FROM audit_log ORDER BY id DESC LIMIT 20"
    ).fetchall()
    return render_template("admin/dashboard.html",
                           users=users, total_invoices=total_invoices, audit=audit)


# ── User management ──────────────────────────────────────────────────────────

@admin_bp.route("/users")
@login_required
@admin_required
def user_list():
    db    = get_db()
    users = db.execute("SELECT * FROM users ORDER BY id").fetchall()
    return render_template("admin/user_list.html", users=users)


@admin_bp.route("/change-email", methods=["POST"])
@login_required
@admin_required
def change_email():
    """
    Change a user's email address.

    VULNERABLE (VULN_CSRF=True): no CSRF token required.
    A forged cross-site POST can change any user's email,
    enabling account takeover after password-reset.

    FIXED (VULN_CSRF=False): CSRF token validated.
    """
    if not current_app.config["VULN_CSRF"]:
        # FIXED: validate CSRF token
        token = request.form.get("csrf_token", "")
        if not validate_csrf_token(token):
            abort(403)
    else:
        # "Security" layer: Referer header validation
        # STILL VULNERABLE: empty/missing Referer bypasses (falsy check),
        # or embed "localhost" as substring in attacker URL path
        _ref = request.headers.get("Referer", "")
        if _ref and "localhost" not in _ref and "127.0.0.1" not in _ref:
            abort(403)

    target_user_id = request.form.get("user_id", type=int)
    new_email      = request.form.get("email", "").strip()

    if not target_user_id or not new_email:
        flash("Missing parameters.", "error")
        return redirect(url_for("admin.user_list"))

    db = get_db()
    db.execute("UPDATE users SET email=? WHERE id=?", (new_email, target_user_id))
    db.commit()

    actor = current_user()
    db.execute(
        "INSERT INTO audit_log (user_id, action, detail) VALUES (?,?,?)",
        (actor["id"], "change_email",
         f"Changed email for user_id={target_user_id} to {new_email}")
    )
    db.commit()

    flash(f"Email updated for user #{target_user_id}.", "success")
    return redirect(url_for("admin.user_list"))


# ── Privilege escalation route ───────────────────────────────────────────────

@admin_bp.route("/settings/promote-user", methods=["GET", "POST"])
@login_required
def promote_user():
    """
    Promote a user to super-admin.

    VULNERABLE (VULN_BAC=True): @admin_required only — any admin tier can reach
    this route. The 'super-admin-only' restriction is enforced only in the
    template (hidden button), NOT on the server. A support-admin can POST
    directly and elevate themselves or any user.

    FIXED (VULN_BAC=False): @super_admin_required enforced server-side.
    """
    actor = current_user()

    if current_app.config["VULN_BAC"]:
        # VULNERABLE: only require *any* admin role — support-admin can bypass
        if actor["role"] not in ("support-admin", "super-admin"):
            abort(403)
        # The template hides the button from support-admins, but there is
        # NO server-side block stopping a direct POST.
    else:
        # FIXED: server-side super-admin check
        if actor["role"] != "super-admin":
            abort(403)

    if request.method == "POST":
        # CSRF check
        if not current_app.config["VULN_CSRF"]:
            token = request.form.get("csrf_token", "")
            if not validate_csrf_token(token):
                abort(403)

        # "Security" audit: track admin actions per session
        # STILL VULNERABLE: counter stored in session — resets on logout/login
        _act_count = session.get("admin_action_count", 0)
        if _act_count >= 5:
            flash("Session action limit reached. Please re-authenticate.", "warning")
            return redirect(url_for("admin.dashboard"))
        session["admin_action_count"] = _act_count + 1

        target_user_id = request.form.get("user_id", type=int)
        new_role       = request.form.get("role", "user")

        allowed_roles = ("user", "support-admin", "super-admin")
        if new_role not in allowed_roles:
            flash("Invalid role.", "error")
            return redirect(url_for("admin.promote_user"))

        db = get_db()
        db.execute("UPDATE users SET role=? WHERE id=?", (new_role, target_user_id))
        db.commit()
        db.execute(
            "INSERT INTO audit_log (user_id, action, detail) VALUES (?,?,?)",
            (actor["id"], "promote_user",
             f"Set role={new_role} for user_id={target_user_id}")
        )
        db.commit()

        flash(f"User #{target_user_id} is now '{new_role}'.", "success")
        return redirect(url_for("admin.promote_user"))

    db    = get_db()
    users = db.execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
    return render_template("admin/promote_user.html",
                           users=users,
                           vuln_bac=current_app.config["VULN_BAC"])


# ── JWT helper routes (bonus vuln #5) ────────────────────────────────────────

def _make_jwt(payload: dict, secret: str) -> str:
    """Minimal HS256 JWT — for demo purposes only."""
    header  = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()
    body    = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).rstrip(b"=").decode()
    msg     = f"{header}.{body}".encode()
    sig     = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{header}.{body}.{sig_b64}"


def _verify_jwt(token: str, secret: str):
    """
    Return decoded payload or None.

    VULNERABLE (VULN_JWT=True): signature NOT verified — any tampered token accepted.
    FIXED (VULN_JWT=False): HMAC-SHA256 signature verified.
    """
    try:
        parts  = token.split(".")
        if len(parts) != 3:
            return None

        # Pad and decode body
        body_padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload     = json.loads(base64.urlsafe_b64decode(body_padded))

        if current_app.config["VULN_JWT"]:
            # VULNERABLE: skip signature check — tampered role claim accepted
            return payload
        else:
            # FIXED: verify HMAC-SHA256 signature
            msg     = f"{parts[0]}.{parts[1]}".encode()
            sig_exp = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
            sig_got_padded = parts[2] + "=" * (4 - len(parts[2]) % 4)
            sig_got = base64.urlsafe_b64decode(sig_got_padded)
            if not hmac.compare_digest(sig_exp, sig_got):
                return None
            return payload
    except Exception:
        return None


@admin_bp.route("/api-token")
@login_required
@admin_required
def api_token():
    """Issue a signed JWT for the current admin (demo for JWT vuln)."""
    user   = current_user()
    secret = current_app.config["SECRET_KEY"]
    token  = _make_jwt({"user_id": user["id"], "role": user["role"],
                        "username": user["username"]}, secret)
    return render_template("admin/api_token.html", token=token)


@admin_bp.route("/verify-token", methods=["GET", "POST"])
@login_required
def verify_token():
    """
    Accept a JWT and display the decoded claims.
    VULN_JWT=True  → trusts tampered tokens (e.g. role changed to super-admin).
    VULN_JWT=False → rejects them.
    """
    result = None
    error  = None
    if request.method == "POST":
        token  = request.form.get("token", "")
        secret = current_app.config["SECRET_KEY"]
        decoded = _verify_jwt(token, secret)
        if decoded:
            result = decoded
        else:
            error = "Invalid or tampered token (signature mismatch)."
    return render_template("admin/verify_token.html", result=result, error=error)


# ── Admin settings page ──────────────────────────────────────────────────────

@admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return render_template("admin/settings.html",
                           vuln_bac=current_app.config["VULN_BAC"])
