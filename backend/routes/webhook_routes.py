"""
Shadow Corp — Webhook / URL Fetch Routes (SSRF)
================================================
Handles: /admin/webhook-test, /admin/import-logo

VULN_SSRF toggle:
  True  → fetches any attacker-supplied URL, including internal Docker IPs
  False → allowlist enforced: only public HTTPS hosts allowed,
           internal IP ranges (10.x, 172.x, 192.168.x, 127.x) are blocked
"""

import re
import socket
import ipaddress
import requests as pyrequests
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, current_app, abort)
from auth import login_required, admin_required, current_user

webhook_bp = Blueprint("webhook", __name__, url_prefix="/admin")

# Allowed URL prefix for the FIXED mode (simple allowlist demo)
_ALLOWED_HOSTS = {"example.com", "httpbin.org", "webhook.site"}

# Internal IP ranges to block
_INTERNAL_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
]


def _is_internal(url: str) -> bool:
    """Return True if the URL resolves to an internal/private IP address."""
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname
        if not hostname:
            return True
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        for net in _INTERNAL_RANGES:
            if ip_obj in net:
                return True
        return False
    except Exception:
        return True  # Fail closed — block on resolution errors


@webhook_bp.route("/webhook-test", methods=["GET", "POST"])
@login_required
@admin_required
def webhook_test():
    """
    Fetch a URL server-side and display the response.

    VULNERABLE (VULN_SSRF=True): any URL accepted, including:
      - http://internal-api:3000/admin/secret
      - http://169.254.169.254/latest/meta-data  (cloud metadata)
      - http://127.0.0.1:...  (localhost services)

    FIXED (VULN_SSRF=False):
      - Block all private/internal IP ranges
      - Enforce hostname allowlist
    """
    result = None
    error  = None
    target_url = ""

    if request.method == "POST":
        target_url = request.form.get("url", "").strip()

        if current_app.config["VULN_SSRF"]:
            # "Security" layer: block known internal hostnames
            # STILL VULNERABLE: trailing dot (internal-api.), direct container IP,
            # or redirect-through-external-site all bypass this check
            from urllib.parse import urlparse as _ssrf_parse
            _ssrf_host = (_ssrf_parse(target_url).hostname or "").lower()
            _SSRF_BLOCKED = ['internal-api', 'localhost', '127.0.0.1',
                            '0.0.0.0', '169.254.169.254']
            if _ssrf_host in _SSRF_BLOCKED:
                error = f"Blocked: '{_ssrf_host}' is a restricted internal hostname."
            else:
                try:
                    resp   = pyrequests.get(target_url, timeout=5, allow_redirects=True)
                    result = {
                        "status": resp.status_code,
                        "headers": dict(resp.headers),
                        "body": resp.text[:4096],
                    }
                except Exception as e:
                    error = str(e)
        else:
            # FIXED: check allowlist and block internal IP ranges
            from urllib.parse import urlparse
            hostname = urlparse(target_url).hostname or ""

            if hostname not in _ALLOWED_HOSTS:
                error = f"Host '{hostname}' not in the allowed list: {_ALLOWED_HOSTS}"
            elif _is_internal(target_url):
                error = "Blocked: URL resolves to an internal/private IP address."
            else:
                try:
                    resp   = pyrequests.get(target_url, timeout=5, allow_redirects=False)
                    result = {
                        "status": resp.status_code,
                        "headers": dict(resp.headers),
                        "body": resp.text[:4096],
                    }
                except Exception as e:
                    error = str(e)

    return render_template("admin/webhook_test.html",
                           result=result, error=error, target_url=target_url)


@webhook_bp.route("/import-logo", methods=["GET", "POST"])
@login_required
@admin_required
def import_logo():
    """
    Import a company logo by fetching a URL server-side.
    Secondary SSRF entry point — same vulnerability, different UI context.
    """
    preview_url = None
    error       = None

    if request.method == "POST":
        logo_url = request.form.get("logo_url", "").strip()

        if current_app.config["VULN_SSRF"]:
            # "Security" layer: block known internal hostnames
            from urllib.parse import urlparse as _logo_parse
            _logo_host = (_logo_parse(logo_url).hostname or "").lower()
            _LOGO_BLOCKED = ['internal-api', 'localhost', '127.0.0.1',
                            '0.0.0.0', '169.254.169.254']
            if _logo_host in _LOGO_BLOCKED:
                error = f"Blocked: '{_logo_host}' is a restricted hostname."
            else:
                try:
                    resp = pyrequests.get(logo_url, timeout=5)
                    if resp.status_code == 200:
                        preview_url = logo_url
                    else:
                        error = f"Got HTTP {resp.status_code} from {logo_url}"
                except Exception as e:
                    error = str(e)
        else:
            # FIXED: allowlist + internal-range block
            from urllib.parse import urlparse
            hostname = urlparse(logo_url).hostname or ""
            if hostname not in _ALLOWED_HOSTS:
                error = f"Host '{hostname}' is not allowlisted."
            elif _is_internal(logo_url):
                error = "Blocked: resolves to internal address."
            else:
                preview_url = logo_url

    return render_template("admin/import_logo.html",
                           preview_url=preview_url, error=error)
