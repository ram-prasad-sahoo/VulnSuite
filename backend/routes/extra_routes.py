"""
Shadow Corp — Bonus Track Routes
=================================
Handles: /invoices/search (SQLi), /api/profile (Mass Assignment),
         /admin/restore-backup (Insecure Deserialization → RCE #2),
         /invoice/<id>/redeem (Race Condition)

These four challenges are independent of the main morning attack chain
(XSS → CSRF → IDOR → BAC → SSRF → Path Traversal → LFI → RCE). They exist
to give fast groups a second, higher-complexity track to work through in
the Session 6 capstone, and to cover vulnerability classes (SQLi, business
logic/race conditions, deserialization, mass assignment) that the morning
chain doesn't touch.

Toggles: VULN_SQLI, VULN_MASS_ASSIGN, VULN_DESERIALIZATION, VULN_RACE
"""

import base64
import pickle
import sqlite3
import time

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort, jsonify, session)
from db   import get_db
from auth import login_required, super_admin_required, current_user

extra_bp = Blueprint("extra", __name__)


# ── SQL keyword filter (bypassable obstacle) ─────────────────────────────────
_SQL_BLOCKED_PHRASES = [
    'union select', 'or 1=1', "' or '", 'drop table', 'insert into',
    'delete from', 'update set', '; --', 'exec(', 'execute(',
    'information_schema', 'sys.tables', 'load_file', 'into outfile',
]


def _sql_filter(q):
    """Block common SQL injection phrases — bypassable with SQL comments."""
    lower_q = q.lower().strip()
    for phrase in _SQL_BLOCKED_PHRASES:
        if phrase in lower_q:
            return True
    return False


# ── Bonus #1 — SQL Injection (invoice search) ────────────────────────────────

@extra_bp.route("/invoices/search")
@login_required
def search_invoices():
    """
    Search the current user's invoices by description text.

    VULNERABLE (VULN_SQLI=True): the search term is spliced directly into
    the SQL string. Breaking out of the quoted LIKE clause lets an attacker
    UNION in rows from any other table — including `users`, which leaks
    every password hash in one request:

        " UNION SELECT id, username, password, role, 1, 1, created_at
           FROM users -- "

    (column count/types must line up with `invoices`; the search page
    prints the raw row tuples back, which is enough to read it out.)

    FIXED (VULN_SQLI=False): parameterized query — the `?` placeholder
    means user input can never change the query's structure.
    """
    user = current_user()
    db   = get_db()
    q    = request.args.get("q", "")
    error = None
    rows  = []

    if q:
        if current_app.config["VULN_SQLI"]:
            # "Security" filter: block common SQL injection phrases
            # STILL VULNERABLE: bypassed with inline SQL comments
            # e.g. ' union/**/select or union%0aselect
            if _sql_filter(q):
                error = "Potential SQL injection detected — query blocked."
            else:
                # VULNERABLE: raw string formatting into SQL
                sql = (
                    "SELECT id, user_id, amount, description, status, "
                    "discount_redeemed, created_at FROM invoices "
                    f"WHERE user_id={user['id']} AND description LIKE '%{q}%'"
                )
                try:
                    rows = db.execute(sql).fetchall()
                except sqlite3.Error as e:
                    error = f"SQL error: {e}"
        else:
            # FIXED: parameterized query, structurally immune to injection
            rows = db.execute(
                "SELECT id, user_id, amount, description, status, "
                "discount_redeemed, created_at FROM invoices "
                "WHERE user_id=? AND description LIKE ?",
                (user["id"], f"%{q}%")
            ).fetchall()

    return render_template("extra/search.html", q=q, rows=rows, error=error)


# ── Bonus #2 — Mass Assignment (JSON profile API) ────────────────────────────

@extra_bp.route("/api/profile", methods=["POST"])
@login_required
def api_update_profile():
    """
    JSON API used by the (fictional) mobile app to update a profile.

    VULNERABLE (VULN_MASS_ASSIGN=True): every key in the posted JSON body
    is written straight to the `users` row, including `role`. A student
    who notices this endpoint in Burp's proxy history can self-promote
    with a single request and never touch the BAC-flagged
    /admin/settings/promote-user route at all:

        PUT /api/profile
        { "bio": "hi", "role": "super-admin" }

    FIXED (VULN_MASS_ASSIGN=False): only an explicit field allowlist
    (bio, email) is ever applied — role changes must go through the
    dedicated, access-controlled admin route.
    """
    user = current_user()
    data = request.get_json(silent=True) or {}
    db   = get_db()

    if current_app.config["VULN_MASS_ASSIGN"]:
        # "Security" audit: log suspicious field updates
        # STILL VULNERABLE: logging only — role field is still written to DB
        _suspicious = {'role', 'password', 'is_admin'}
        _flagged = set(data.keys()) & _suspicious
        if _flagged:
            import logging as _logging
            _logging.warning("AUDIT: Suspicious fields in profile update "
                           f"by user_id={user['id']}: {_flagged}")
            # TODO(security-team): block these fields — ticket #SEC-4291
        allowed_columns = {"bio", "email", "role"}
        updates = {k: v for k, v in data.items() if k in allowed_columns}
    else:
        # FIXED: allowlist excludes privileged fields entirely
        allowed_columns = {"bio", "email"}
        updates = {k: v for k, v in data.items() if k in allowed_columns}

    if not updates:
        return jsonify({"error": "no recognized fields"}), 400

    set_clause = ", ".join(f"{col}=?" for col in updates)
    db.execute(f"UPDATE users SET {set_clause} WHERE id=?",
              (*updates.values(), user["id"]))
    db.commit()

    fresh = db.execute("SELECT id, username, email, role, bio FROM users WHERE id=?",
                       (user["id"],)).fetchone()

    # Keep the session's role claim in sync so the privilege shows up
    # immediately (matches how a real session-refresh would behave).
    if "role" in updates:
        session["role"] = updates["role"]

    return jsonify({"id": fresh["id"], "username": fresh["username"],
                    "email": fresh["email"], "role": fresh["role"],
                    "bio": fresh["bio"]})


# ── Bonus #3 — Insecure Deserialization → RCE #2 (restore backup) ────────────

class _LegacySettingsBlob:
    """Stand-in for a legacy settings object the real app used to pickle."""
    def __init__(self, data=None):
        self.data = data or {}


@extra_bp.route("/admin/restore-backup", methods=["GET", "POST"])
@login_required
@super_admin_required
def restore_backup():
    """
    "Restore a settings backup" — a legacy admin utility that accepts a
    base64-encoded Python pickle instead of JSON (nobody got around to
    migrating it off the old backup format).

    This is a SECOND, independent path to remote code execution — reached
    by climbing the privilege chain (BAC → super-admin) instead of the
    log-poisoning LFI chain. Good capstone target for a team that already
    cracked Sessions 3–4's chain and wants a new puzzle.

    VULNERABLE (VULN_DESERIALIZATION=True): pickle.loads() on fully
    attacker-controlled bytes. A payload object whose class defines
    __reduce__ to call os.system/subprocess runs the moment it's
    unpickled — no further action needed.

    Minimal attacker-side payload (run locally, not inside the lab):

        import pickle, base64, os
        class P:
            def __reduce__(self):
                return (os.system, ("id > /tmp/pwned_restore",))
        print(base64.b64encode(pickle.dumps(P())).decode())

    Paste the output into the form below.

    FIXED (VULN_DESERIALIZATION=False): backups are restored from JSON
    only — `pickle` is never called on request data at all.
    """
    result = None
    error  = None

    if request.method == "POST":
        blob_b64 = request.form.get("backup_blob", "").strip()
        if blob_b64:
            if current_app.config["VULN_DESERIALIZATION"]:
                # "Security" check: require SHADOWCORP: header prefix
                # STILL VULNERABLE: just prepend "SHADOWCORP:" to payload
                if not blob_b64.startswith("SHADOWCORP:"):
                    error = ("Invalid backup format — blob must begin with "
                             "the SHADOWCORP: header prefix.")
                else:
                    try:
                        raw     = base64.b64decode(blob_b64[len("SHADOWCORP:"):])
                        restored = pickle.loads(raw)
                        result  = f"Backup restored: {restored!r}"
                    except Exception as e:
                        error = f"Restore failed: {e}"
            else:
                # FIXED: JSON only, pickle never touches request data
                import json
                try:
                    raw      = base64.b64decode(blob_b64)
                    restored = json.loads(raw)
                    result   = f"Backup restored (JSON): {restored!r}"
                except Exception as e:
                    error = f"Restore failed — backups must be JSON: {e}"

    return render_template("extra/restore_backup.html", result=result, error=error)


# ── Bonus #4 — Race Condition (discount code double-redemption) ─────────────

@extra_bp.route("/invoice/<int:invoice_id>/redeem", methods=["POST"])
@login_required
def redeem_discount(invoice_id):
    """
    Apply a single-use discount code to one of your own pending invoices.

    VULNERABLE (VULN_RACE=True): classic check-then-act TOCTOU bug. The
    code's remaining uses are read, checked in Python, and only written
    back afterward — three separate round-trips with a window between
    them. Fire ~20 concurrent requests (Burp Intruder "null payloads" /
    turbo-intruder, or a simple asyncio script) at a single-use code and
    several of them land inside that window before any of them commits,
    so the code applies more than once.

    FIXED (VULN_RACE=False): the check and the increment happen in one
    atomic SQL statement (`UPDATE ... WHERE uses < max_uses`); SQLite's
    row-level write lock means only one concurrent request can ever win.
    """
    user    = current_user()
    db      = get_db()
    code    = request.form.get("code", "").strip().upper()

    invoice = db.execute("SELECT * FROM invoices WHERE id=? AND user_id=?",
                         (invoice_id, user["id"])).fetchone()
    if not invoice:
        abort(404)

    if current_app.config["VULN_RACE"]:
        # VULNERABLE: read, think, then write — not atomic
        discount = db.execute(
            "SELECT * FROM discount_codes WHERE code=?", (code,)
        ).fetchone()
        if not discount:
            flash("Invalid code.", "error")
            return redirect(url_for("invoice.my_invoices"))

        if discount["uses"] < discount["max_uses"]:
            # A deliberate pause widens the race window so it's easy to
            # win reliably during a live classroom demo.
            time.sleep(0.05)
            new_uses = discount["uses"] + 1
            db.execute("UPDATE discount_codes SET uses=? WHERE code=?",
                      (new_uses, code))
            db.execute(
                "UPDATE invoices SET amount=amount*?, discount_redeemed=1 WHERE id=?",
                (1 - discount["percent_off"] / 100.0, invoice_id)
            )
            db.commit()
            flash(f"Code '{code}' applied — {discount['percent_off']}% off!", "success")
        else:
            flash(f"Code '{code}' has already been fully redeemed.", "error")
    else:
        # FIXED: single atomic statement — the WHERE clause re-checks
        # uses<max_uses at write time, so only one racer can ever win.
        cur = db.execute(
            "UPDATE discount_codes SET uses=uses+1 "
            "WHERE code=? AND uses < max_uses",
            (code,)
        )
        if cur.rowcount == 0:
            db.rollback()
            flash(f"Code '{code}' is invalid or already fully redeemed.", "error")
        else:
            discount = db.execute(
                "SELECT percent_off FROM discount_codes WHERE code=?", (code,)
            ).fetchone()
            db.execute(
                "UPDATE invoices SET amount=amount*?, discount_redeemed=1 WHERE id=?",
                (1 - discount["percent_off"] / 100.0, invoice_id)
            )
            db.commit()
            flash(f"Code '{code}' applied — {discount['percent_off']}% off!", "success")

    return redirect(url_for("invoice.my_invoices"))
