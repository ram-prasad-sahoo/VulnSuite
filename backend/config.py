"""
Shadow Corp — Vulnerability Configuration
==========================================
Each VULN_* flag enables/disables a specific vulnerability.
Set to True  → vulnerable (demo attack)
Set to False → fixed     (demo defense)

Override via environment variables, e.g.:
    VULN_XSS=false docker-compose up
"""

import os


def _bool(env_key: str, default: bool) -> bool:
    """Read an env var as a boolean, falling back to the given default."""
    val = os.environ.get(env_key)
    if val is None:
        return default
    return val.strip().lower() not in ("0", "false", "no", "off")


class Config:
    # ── Flask core ──────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "shadow-corp-insecure-dev-key-DO-NOT-USE")
    DATABASE    = os.environ.get("DATABASE", "LabDatabase.db")
    DEBUG       = _bool("FLASK_DEBUG", True)

    # ── Vulnerability toggles ───────────────────────────────────────────────
    # 1. Stored XSS — bio field rendered without HTML encoding
    VULN_XSS   = _bool("VULN_XSS",   True)

    # Content filter in front of the bio field — see waf.py. Only matters
    # while VULN_XSS is also True; adds an encoding-bypass puzzle on top
    # of the base stored-XSS bug. Default on, so the harder path is what
    # a fresh checkout demonstrates; flip off for an easier/faster demo.
    WAF_ENABLED = _bool("WAF_ENABLED", True)

    # 2. CSRF — no CSRF tokens + SameSite=None on session cookie
    VULN_CSRF  = _bool("VULN_CSRF",  True)

    # 3. IDOR — invoice/user lookup ignores ownership
    VULN_IDOR  = _bool("VULN_IDOR",  True)

    # 4. Broken Access Control — role check absent on admin-only routes
    VULN_BAC   = _bool("VULN_BAC",   True)

    # 5. JWT role tampering — signature verification disabled
    VULN_JWT   = _bool("VULN_JWT",   True)

    # 6. SSRF — webhook/import-URL fetches any attacker-supplied URL
    VULN_SSRF  = _bool("VULN_SSRF",  True)

    # 7. Path Traversal — document viewer doesn't jail-check the path
    VULN_PATH_TRAVERSAL = _bool("VULN_PATH_TRAVERSAL", True)

    # 8. LFI — page renderer dynamically includes arbitrary files
    VULN_LFI   = _bool("VULN_LFI",   True)

    # 9. RCE via File Upload (chain through LFI & template execution)
    VULN_RCE   = _bool("VULN_RCE",   True)

    # ── Bonus track (higher-complexity, independent challenges) ─────────────
    # 10. SQL Injection — invoice search concatenates the query raw into SQL
    VULN_SQLI  = _bool("VULN_SQLI",  True)

    # 11. Mass Assignment — JSON profile API accepts a client-supplied 'role'
    VULN_MASS_ASSIGN = _bool("VULN_MASS_ASSIGN", True)

    # 12. Insecure Deserialization — "restore backup" unpickles attacker data
    VULN_DESERIALIZATION = _bool("VULN_DESERIALIZATION", True)

    # 13. Race Condition — discount code can be redeemed more than once
    VULN_RACE  = _bool("VULN_RACE",  True)

    # 14. Open Redirect — post-login ?next= is followed with no validation
    VULN_OPEN_REDIRECT = _bool("VULN_OPEN_REDIRECT", True)

    # ── Internal microservice URL (Docker network) ──────────────────────────
    INTERNAL_API_URL = os.environ.get("INTERNAL_API_URL", "http://internal-api:3000")

    # ── Session cookie settings ─────────────────────────────────────────────
    # VULNERABLE: SameSite=None allows cross-site requests (aids CSRF)
    # FIXED:      SESSION_COOKIE_SAMESITE = "Strict"
    if not _bool("VULN_CSRF", True):
        SESSION_COOKIE_SAMESITE = "Strict"
    
    SESSION_COOKIE_SECURE   = False   # HTTP only in the lab
    SESSION_COOKIE_HTTPONLY = True
