"""
Shadow Corp — Document / Path Traversal Routes
===============================================
Handles: /documents/view

VULN_PATH_TRAVERSAL toggle:
  True  → filename parameter used raw — ../ traversal reads any file on the server
  False → realpath check ensures file is inside the allowed documents/ directory
"""

import os
from flask import (Blueprint, render_template, request, current_app,
                   abort, Response)
from auth import login_required

document_bp = Blueprint("document", __name__)

# Allowed base directory for documents
_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")


@document_bp.route("/documents/view")
@login_required
def view_document():
    """
    Serve a file from the documents/ directory.

    VULNERABLE (VULN_PATH_TRAVERSAL=True):
        ?filename=../../etc/passwd           → reads /etc/passwd
        ?filename=../../app.py               → reads source code
        ?filename=../../logs/access.log      → reads the request log (needed for RCE)
        ?filename=../config.py               → reads Flask secret key etc.

    FIXED (VULN_PATH_TRAVERSAL=False):
        os.path.realpath() is used to resolve symlinks and ../ sequences;
        the result is checked to ensure it still starts with _DOCS_DIR.
    """
    filename = request.args.get("filename", "")

    if not filename:
        # Show document listing
        try:
            files = os.listdir(_DOCS_DIR)
        except FileNotFoundError:
            files = []
        return render_template("document/document_list.html", files=files)

    if current_app.config["VULN_PATH_TRAVERSAL"]:
        # "Security" filter: strip path-traversal sequences (single pass)
        # STILL VULNERABLE: ....// → after removing ../ from middle → ../
        sanitized = filename.replace("../", "").replace("..\\", "")
        target_path = os.path.join(_DOCS_DIR, sanitized)
    else:
        # FIXED: resolve absolute path and ensure it stays inside _DOCS_DIR
        target_path = os.path.realpath(os.path.join(_DOCS_DIR, filename))
        real_docs   = os.path.realpath(_DOCS_DIR)
        if not target_path.startswith(real_docs + os.sep) and target_path != real_docs:
            abort(403)   # Jail escape detected

    try:
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return render_template("document/view_document.html",
                               filename=filename,
                               content=content,
                               path=target_path)
    except FileNotFoundError:
        abort(404)
    except PermissionError:
        abort(403)
    except IsADirectoryError:
        abort(400)
