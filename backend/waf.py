"""
Shadow Corp — Lightweight Input Filter ("WAF-lite")
====================================================
A simple perimeter content filter applied to the profile bio field.

It turns the stored-XSS challenge (profile_routes.py, VULN_XSS) into a
multi-step puzzle instead of a one-shot `<script>` paste: a naive payload,
and the two most common "quick obfuscations" people reach for first
(base64-wrapping the whole payload, or URL-encoding it), are all caught.

The gap: this filter only ever tries ONE decoding pass of ONE scheme, and
it never decodes HTML character references at all. A payload built out of
HTML entities (decimal `&#60;...&#62;` or hex `&#x3c;...&#x3e;`) — or one
where only the keywords the blocklist is watching for are entity-encoded,
with the rest left as plain characters — sails straight through this
filter untouched, because the literal string never contains "<script" or
"onerror=" etc. It only becomes a real `<script>` tag (or event handler)
the moment the BROWSER's own HTML parser renders the stored bio with
`|safe` and decodes those entities itself — which happens entirely on the
read side, downstream of anything this filter ever sees.

Toggle: WAF_ENABLED (config.py) — only meaningful while VULN_XSS is also
True; if XSS is already fixed (output is HTML-escaped), this filter does
nothing an attacker could use anyway.
"""

import re
import base64
import urllib.parse

_BLOCKLIST = [
    r"<\s*script",
    r"javascript\s*:",
    r"on[a-z]+\s*=",          # onerror=, onload=, onclick=, onmouseover=, ...
    r"<\s*iframe",
    r"<\s*svg",
    r"<\s*object",
    r"<\s*embed",
    r"<\s*img",
    r"<\s*body",
    r"<\s*details",
    r"<\s*math",
    r"<\s*marquee",
    r"<\s*video",
    r"<\s*audio",
    r"<\s*input",
    r"<\s*textarea",
    r"<\s*form",
    r"<\s*base",
    r"<\s*link",
    r"document\s*\.\s*cookie",
    r"document\s*\.\s*location",
    r"window\s*\.\s*location",
    r"alert\s*\(",
    r"prompt\s*\(",
    r"confirm\s*\(",
    r"eval\s*\(",
    r"fetch\s*\(",
    r"XMLHttpRequest",
    r"String\.fromCharCode",
    r"atob\s*\(",
]

_BLOCKLIST_RE = re.compile("|".join(_BLOCKLIST), re.IGNORECASE)


def _hits_blocklist(text: str) -> bool:
    return bool(_BLOCKLIST_RE.search(text))


def is_blocked(raw_text: str) -> bool:
    """
    True if `raw_text` — or a single decoding of it — matches the
    blocklist above.

    Deliberately shallow by design: exactly one decode attempt per scheme,
    no recursion, no HTML-entity awareness. That shallowness is the gap
    the harder encoding techniques (HTML entities, partial/mixed entity
    encoding of just the trigger keywords) are meant to exploit.
    """
    if not raw_text:
        return False

    if _hits_blocklist(raw_text):
        return True

    # Single-pass URL-decode — catches "%3Cscript%3E..." style payloads.
    try:
        url_decoded = urllib.parse.unquote(raw_text)
        if url_decoded != raw_text and _hits_blocklist(url_decoded):
            return True
    except Exception:
        pass

    # Double URL-decode pass — catches %253Cscript%253E style payloads
    try:
        double_decoded = urllib.parse.unquote(urllib.parse.unquote(raw_text))
        if double_decoded != raw_text and double_decoded != url_decoded and _hits_blocklist(double_decoded):
            return True
    except Exception:
        pass

    # Single-pass base64-decode, only attempted when the *entire* field
    # looks like a base64 blob — catches base64("<script>...") payloads.
    candidate = raw_text.strip()
    if re.fullmatch(r"[A-Za-z0-9+/]{8,}={0,2}", candidate):
        try:
            padded  = candidate + "=" * (-len(candidate) % 4)
            decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
            if _hits_blocklist(decoded):
                return True
        except Exception:
            pass

    return False
