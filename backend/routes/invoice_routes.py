"""
VulnSuite — Invoice Routes
=============================
Handles: /invoice/<id>, /invoices

VULN_IDOR toggle:
  True  → no ownership check; any user can view any invoice by ID
  False → verify invoice.user_id == session user_id
"""

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort)
from db   import get_db
from auth import login_required, current_user

invoice_bp = Blueprint("invoice", __name__)


@invoice_bp.route("/invoices")
@login_required
def my_invoices():
    """Show the logged-in user's own invoices."""
    user     = current_user()
    db       = get_db()
    invoices = db.execute(
        "SELECT * FROM invoices WHERE user_id=? ORDER BY id DESC", (user["id"],)
    ).fetchall()
    return render_template("invoice/my_invoices.html", invoices=invoices)


@invoice_bp.route("/invoice/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):
    """
    View a single invoice by numeric ID.

    VULNERABLE (VULN_IDOR=True): NO ownership check.
    Any authenticated user can enumerate IDs to read others' invoices.

    FIXED (VULN_IDOR=False): enforce ownership — 403 if user doesn't own it.
    """
    user    = current_user()
    db      = get_db()
    invoice = db.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()

    if not invoice:
        abort(404)

    if not current_app.config["VULN_IDOR"]:
        # FIXED: ownership check
        if invoice["user_id"] != user["id"] and user["role"] not in ("support-admin", "super-admin"):
            abort(403)
    else:
        # "Security" layer: verify access token for cross-account viewing
        # STILL VULNERABLE: token is simply md5(id)[:8] (predictable, no secret)
        if invoice["user_id"] != user["id"] and user["role"] not in ("support-admin", "super-admin"):
            import hashlib as _hl
            _expected = _hl.md5(str(invoice_id).encode()).hexdigest()[:8]
            if request.args.get("token", "") != _expected:
                abort(403)
    # VULNERABLE: ownership check omitted when token matches

    import hashlib as _hl
    token = _hl.md5(str(invoice_id).encode()).hexdigest()[:8]
    owner = db.execute("SELECT username, email FROM users WHERE id=?",
                       (invoice["user_id"],)).fetchone()
    return render_template("invoice/view_invoice.html",
                           invoice=invoice, owner=owner, token=token)


@invoice_bp.route("/user/<int:user_id>")
@login_required
def view_user_record(user_id):
    """
    Admin-style user lookup by numeric ID.

    VULNERABLE (VULN_IDOR=True): any logged-in user can look up any user's record.
    FIXED (VULN_IDOR=False): must be admin OR own that record.
    """
    user = current_user()
    db   = get_db()

    if not current_app.config["VULN_IDOR"]:
        # FIXED: only admins or self
        if user["id"] != user_id and user["role"] not in ("support-admin", "super-admin"):
            abort(403)
    else:
        # "Security" layer: verify access token for other users (no secret — just md5 of ID)
        if user["id"] != user_id and user["role"] not in ("support-admin", "super-admin"):
            import hashlib as _hl
            _expected = _hl.md5(str(user_id).encode()).hexdigest()[:8]
            if request.args.get("token", "") != _expected:
                abort(403)
    # VULNERABLE: ownership check omitted when token matches

    target = db.execute("SELECT id, username, email, role, bio, created_at FROM users WHERE id=?",
                        (user_id,)).fetchone()
    if not target:
        abort(404)

    invoices = db.execute(
        "SELECT * FROM invoices WHERE user_id=? ORDER BY id DESC", (user_id,)
    ).fetchall()
    return render_template("invoice/user_record.html",
                           target=target, invoices=invoices)
