"""
VulnSuite — File Upload Routes (RCE via File Upload)
=======================================================
Handles: /admin/upload-report

This is the FINAL stage of the main attack chain. Instead of log poisoning,
the attacker uploads a crafted file through this admin endpoint, then uses
the LFI vulnerability (page_routes.py, VULN_LFI) to include the uploaded
file. When VULN_RCE is also True, the included file is rendered as a Jinja2
template — any {{ }} expression in the uploaded file gets executed as Python.

RCE CHAIN:
    1. Gain admin access (via BAC/privilege escalation)
    2. Upload a ".txt" file containing Jinja2 SSTI payload through
       /admin/upload-report
       The file passes all "security" checks because:
         - Extension is .txt (allowed)
         - Python keywords like "import", "os.system" are NOT present
           (Jinja2 SSTI uses __globals__ / lipsum / cycler instead)
         - Content starts with printable ASCII (satisfied)
         - File is under 8KB (satisfied)
    3. Use LFI: GET /pages/render?page=../../uploads/<filename>
       to include the uploaded file
    4. render_template_string() executes the Jinja2 payload → RCE

Obstacles (bypassable):
    - Extension whitelist: only .txt, .csv, .log, .md allowed
      → .txt is allowed, and that's all you need
    - Python code scanner: blocks "import ", "os.system", "subprocess",
      "exec(", "eval(", "__import__", "open("
      → Jinja2 SSTI doesn't use any of these directly — it accesses
        os.popen via lipsum.__globals__ or config.__class__.__init__
    - File size limit: 8KB max
      → SSTI payloads are tiny (under 200 bytes)
    - Content must start with a printable ASCII character
      → trivially satisfied by adding a comment/text line first

FIXED (VULN_RCE=False): uploaded files are stored with a random UUID name
and NEVER served back or included anywhere — the LFI→RCE chain breaks
because render_template_string is not called on included files.

Toggle: VULN_RCE (config.py)
"""

import os
import re
import uuid
from datetime import datetime

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort)
from auth import login_required, admin_required, current_user

upload_bp = Blueprint("upload", __name__)

_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# ── "Security" filters (all bypassable) ─────────────────────────────────────

_ALLOWED_EXTENSIONS = {".txt", ".csv", ".log", ".md"}

# Python code patterns to "detect" malicious uploads
# STILL VULNERABLE: Jinja2 SSTI doesn't use any of these keywords
_DANGEROUS_PATTERNS = [
    r'\bimport\s+',             # "import os", "import subprocess"
    r'\bos\.system\s*\(',       # os.system("cmd")
    r'\bsubprocess\b',          # subprocess.Popen, subprocess.run
    r'\bexec\s*\(',             # exec("code")
    r'\beval\s*\(',             # eval("expression")
    r'\b__import__\s*\(',       # __import__("os")
    r'\bopen\s*\(',             # open("/etc/passwd")
    r'\bcompile\s*\(',          # compile("code", ...)
    r'\bgetattr\s*\(',          # getattr(obj, "attr")
]

_DANGEROUS_RE = re.compile("|".join(_DANGEROUS_PATTERNS), re.IGNORECASE)

_MAX_FILE_SIZE = 8 * 1024   # 8 KB


def _check_extension(filename):
    """Check if file extension is in the allowlist."""
    _, ext = os.path.splitext(filename.lower())
    return ext in _ALLOWED_EXTENSIONS


def _scan_content(content):
    """
    Scan file content for Python code patterns.

    STILL VULNERABLE: this only catches direct Python syntax like
    'import os', 'os.system()', 'exec()', etc.

    Jinja2 SSTI payloads like:
        {{ lipsum.__globals__['os'].popen('id').read() }}
        {{ cycler.__init__.__globals__.os.popen('whoami').read() }}
        {{ config.__class__.__init__.__globals__['os'].popen('ls').read() }}

    use NONE of these keywords — they access the os module through
    Python's MRO / __globals__ chain, completely bypassing this scanner.
    """
    return bool(_DANGEROUS_RE.search(content))


def _is_printable_start(content):
    """File must start with a printable ASCII character."""
    if not content:
        return False
    return content[0].isprintable()


# ── Upload route ─────────────────────────────────────────────────────────────

@upload_bp.route("/admin/upload-report", methods=["GET", "POST"])
@login_required
@admin_required
def upload_report():
    """
    Upload an incident report file.

    VULNERABLE (VULN_RCE=True): files are saved with their original name
    into the uploads/ directory. The "security" checks (extension, content
    scan, size, printable check) can all be bypassed with a .txt file
    containing Jinja2 SSTI payload.

    Combined with VULN_LFI=True, an attacker can include the uploaded file
    via /pages/render?page=../../uploads/<filename> and get RCE.

    FIXED (VULN_RCE=False): files are renamed to a random UUID, stored
    outside the web-accessible path, and NEVER passed to
    render_template_string — breaking the entire RCE chain.
    """
    uploaded_files = []
    error = None

    # List existing uploads for display
    os.makedirs(_UPLOAD_DIR, exist_ok=True)
    try:
        existing_files = sorted(os.listdir(_UPLOAD_DIR))
    except OSError:
        existing_files = []

    if request.method == "POST":
        f = request.files.get("report_file")
        if not f or not f.filename:
            error = "No file selected."
        else:
            filename = f.filename.strip()

            # ── Obstacle 1: Extension whitelist ──────────────────────────
            if not _check_extension(filename):
                error = (f"File type not allowed. Only these extensions are "
                         f"accepted: {', '.join(sorted(_ALLOWED_EXTENSIONS))}")

            # ── Obstacle 2: File size check ──────────────────────────────
            if not error:
                content_bytes = f.read()
                if len(content_bytes) > _MAX_FILE_SIZE:
                    error = (f"File too large ({len(content_bytes)} bytes). "
                             f"Maximum allowed: {_MAX_FILE_SIZE} bytes.")

            # ── Obstacle 3: Printable ASCII start ────────────────────────
            if not error:
                try:
                    content_text = content_bytes.decode("utf-8", errors="replace")
                except Exception:
                    content_text = content_bytes.decode("latin-1")

                if not _is_printable_start(content_text):
                    error = ("Invalid file format: file must start with a "
                             "printable ASCII character.")

            # ── Obstacle 4: Python code pattern scanner ──────────────────
            if not error:
                if _scan_content(content_text):
                    error = ("⚠ Security scan BLOCKED: file contains "
                             "potentially dangerous code patterns "
                             "(Python imports, exec, eval, etc.). "
                             "Please upload a clean report file.")

            # ── Save the file ────────────────────────────────────────────
            if not error:
                if current_app.config["VULN_RCE"]:
                    # VULNERABLE: save with original filename — predictable path
                    # Combined with LFI, attacker can include this file
                    # and render_template_string() will execute any {{ }}
                    safe_name = filename.replace("..", "").replace("/", "_").replace("\\", "_")
                    # "Security": strip ../ from filename (single pass)
                    # STILL VULNERABLE: the file lands in uploads/ with a
                    # known name, and LFI can traverse to it
                    save_path = os.path.join(_UPLOAD_DIR, safe_name)
                    with open(save_path, "wb") as out:
                        out.write(content_bytes)

                    flash(f"Report '{safe_name}' uploaded successfully.", "success")
                    # Refresh file listing
                    existing_files = sorted(os.listdir(_UPLOAD_DIR))
                else:
                    # FIXED: random UUID filename — attacker can't predict
                    # the path, and files are never template-rendered
                    random_name = f"{uuid.uuid4().hex}_{filename}"
                    save_path = os.path.join(_UPLOAD_DIR, random_name)
                    with open(save_path, "wb") as out:
                        out.write(content_bytes)

                    flash(f"Report uploaded securely as '{random_name}'.", "success")
                    existing_files = sorted(os.listdir(_UPLOAD_DIR))

    return render_template("admin/upload_report.html",
                           files=existing_files, error=error)
