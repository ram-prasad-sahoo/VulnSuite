"""
Shadow Corp — Page / LFI / RCE Routes
=======================================
Handles: /pages/render

VULN_LFI toggle:
  True  → ?page= parameter used to open() + exec() arbitrary files
  False → strict allowlist of page names; dynamic path rejected

VULN_RCE toggle (compound with VULN_LFI):
  Both True → uploaded reports in uploads/ can be included and executed:
    1. Attacker uploads a .txt report via /admin/upload-report with template syntax.
    2. Then: GET /pages/render?page=welcome/../../uploads/<filename>
       executes the uploaded file content as a Jinja2 template.

  VULN_RCE=False or VULN_LFI=False: neither step works.
"""

import os
from flask import (Blueprint, render_template, render_template_string,
                   request, current_app, abort)
from auth import login_required

page_bp = Blueprint("page", __name__)

_PAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")

# Strict allowlist for the FIXED mode
_ALLOWED_PAGES = {"welcome", "about", "help", "faq"}


@page_bp.route("/pages/render")
@login_required
def render_page():
    """
    Dynamic page renderer.

    VULNERABLE (VULN_LFI=True):
        ?page=../../etc/passwd            → file read via LFI
        ?page=../../logs/access.log      → if VULN_RCE=True, executes injected
                                           Python template code from poisoned log

    FIXED (VULN_LFI=False):
        Only pages in _ALLOWED_PAGES are accepted.
        No dynamic file paths — no ../ traversal possible.
    """
    page = request.args.get("page", "welcome")

    if current_app.config["VULN_LFI"]:
        # "Security" check: page name must begin with an alphabetic character
        # STILL VULNERABLE: pages/../../logs/access.log starts with 'p'
        if not page or not page[0].isalpha():
            abort(403)
        # VULNERABLE: dynamic file inclusion — path not fully restricted
        page_path = os.path.join(_PAGES_DIR, page)

        # Also allow traversal out of pages/ (combines with path traversal)
        try:
            with open(page_path, "r", encoding="utf-8", errors="replace") as f:
                raw_content = f.read()
        except FileNotFoundError:
            abort(404)
        except (PermissionError, IsADirectoryError):
            abort(403)

        if current_app.config["VULN_RCE"]:
            # VULNERABLE: render file content as a Jinja2 template string —
            # any {{ }} expression in the file (e.g. from a poisoned log) is executed.
            # RCE CHAIN:
            #   1. Send: User-Agent: {{lipsum.__globals__['os'].popen('id').read()}}
            #   2. GET /pages/render?page=../../logs/access.log
            try:
                return render_template_string(raw_content)
            except Exception as e:
                return f"<pre>Template error: {e}</pre>", 500
        else:
            # LFI only — file read without execution
            return render_template("page/page_view.html",
                                   page=page, content=raw_content)
    else:
        # FIXED: strict allowlist — only known page names accepted
        safe_name = os.path.basename(page)  # strip any path components
        if safe_name not in _ALLOWED_PAGES:
            abort(403)

        page_path = os.path.join(_PAGES_DIR, safe_name + ".html")
        try:
            return render_template(f"pages/{safe_name}.html")
        except Exception:
            abort(404)
