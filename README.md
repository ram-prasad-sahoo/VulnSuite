# Shadow Corp — Cybersecurity Training Lab

> ⚠️ **EDUCATIONAL USE ONLY** — This application is **deliberately vulnerable**.  
> Never deploy it on a public network or production environment.  
> Designed for isolated, local-only classroom demonstrations.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Lab Credentials](#lab-credentials)
3. [Vulnerability Toggle Reference](#vulnerability-toggle-reference)
4. [Full Attack Chain Walkthrough](#full-attack-chain-walkthrough)
   - [Stage 1 — Stored XSS](#stage-1--stored-xss)
   - [Stage 2 — CSRF → Account Takeover](#stage-2--csrf--account-takeover)
   - [Stage 3 — IDOR](#stage-3--idor)
   - [Stage 4 — Broken Access Control](#stage-4--broken-access-control)
   - [Stage 5 — Privilege Escalation (BAC)](#stage-5--privilege-escalation-bac)
   - [Stage 6 — SSRF](#stage-6--ssrf)
   - [Stage 7 — Path Traversal](#stage-7--path-traversal)
   - [Stage 8 — LFI](#stage-8--lfi)
   - [Stage 9 — RCE via File Upload & Template Execution](#stage-9--rce-via-file-upload--template-execution)
   - [Bonus — JWT Role Tampering](#bonus--jwt-role-tampering)
5. [Harder Mode — WAF-lite Filter on the XSS Stage](#harder-mode--waf-lite-filter-on-the-xss-stage)
6. [Bonus Track — Four Independent Challenges](#bonus-track--four-independent-challenges)
7. [Flipping Flags (Live Fix Demo)](#flipping-flags-live-fix-demo)
8. [Architecture](#architecture)

---

## Quick Start

```bash
# Clone / open the shadowcorp/ directory
cd shadowcorp

# Build and start everything (all vulns ON by default)
docker-compose up --build

# App available at:
#   http://localhost:5000
```

The seed script runs automatically on first start, creating all accounts and sample data.

To **reset** the database to a clean state:

```bash
docker-compose down -v
docker-compose up --build
```

---

## Lab Credentials

| Username        | Password        | Role           |
|-----------------|-----------------|----------------|
| `alice`         | `Password123!`  | user           |
| `bob`           | `Password123!`  | user           |
| `carol`         | `Password123!`  | user           |
| `dave`          | `Password123!`  | user           |
| `eve`           | `Password123!`  | user           |
| `support_admin` | `Admin@Shadow1` | support-admin  |
| `superadmin`    | `Super@Shadow1` | super-admin    |

> **Sequential User IDs**: alice=1, bob=2, carol=3, dave=4, eve=5, support_admin=6, superadmin=7  
> **Invoice IDs** start at 1 and are globally sequential.

---

## Vulnerability Toggle Reference

All flags default to `true` (vulnerable). Flip any to `false` to demo the fix.

| Flag                  | What it controls                                              |
|-----------------------|---------------------------------------------------------------|
| `VULN_XSS`            | Bio + website fields render raw HTML (`\|safe`) vs. HTML-escaped |
| `WAF_ENABLED`         | A content filter sits in front of both fields vs. no filter at all |
| `VULN_CSRF`           | No CSRF token + SameSite=None vs. token + SameSite=Strict     |
| `VULN_IDOR`           | Invoice/user lookup ignores ownership vs. enforces it         |
| `VULN_BAC`            | Promote-user route checks any-admin vs. super-admin only      |
| `VULN_JWT`            | JWT signature verification disabled vs. enabled               |
| `VULN_SSRF`           | URL fetch has no restrictions vs. allowlist + IP block        |
| `VULN_PATH_TRAVERSAL` | Document path not jailed vs. realpath check                   |
| `VULN_LFI`            | Page renderer opens arbitrary files vs. allowlist only        |
| `VULN_RCE`            | Included file executed as Jinja2 template vs. static read     |
| `VULN_SQLI`           | Invoice search builds raw SQL vs. parameterized query          |
| `VULN_MASS_ASSIGN`    | `/api/profile` writes any posted field vs. an explicit allowlist |
| `VULN_DESERIALIZATION`| Backup restore unpickles data vs. JSON-only                   |
| `VULN_RACE`           | Discount redemption has a check-then-act gap vs. one atomic SQL statement |
| `VULN_OPEN_REDIRECT`  | `?next=` followed unconditionally vs. same-site-only           |

**Single-flag override:**
```bash
VULN_XSS=false docker-compose up
```

**Flip all off at once (fully patched):**
```bash
VULN_XSS=false VULN_CSRF=false VULN_IDOR=false VULN_BAC=false \
VULN_JWT=false VULN_SSRF=false VULN_PATH_TRAVERSAL=false \
VULN_LFI=false VULN_RCE=false docker-compose up
```

## Harder Mode — WAF-lite Filter on the XSS Stage

`WAF_ENABLED` (default `true`, only matters while `VULN_XSS` is also `true`)
adds a content filter in front of the profile's **Bio** and **Website**
fields (`backend/waf.py`), so Stage 1 is no longer a one-shot
`<script>` paste:

1. A plain `<script>...`, `onerror=...`, `javascript:...` etc. payload —
   **blocked**.
2. The same payload base64-encoded — **blocked** (the filter tries one
   base64-decode pass and checks the result too).
3. The same payload URL-encoded — **blocked** (one URL-decode pass,
   same idea).
4. The same scheme, HTML-entity-encoded — **decimal `&#106;avascript:` or
   hex `&#x6a;avascript:`** — **gets through**, because the filter never
   decodes HTML character references at all.

The catch students need to discover themselves: the entity-encoding
bypass only actually *executes* anything on the **Website** field, not
the **Bio** field. Bio is rendered as plain page body text — browsers do
not re-parse entity-decoded `<` characters as new tags there, so an
entity-encoded `<script>` in Bio just displays as inert text, same as the
fixed version would. Website is rendered inside an `<a href="...">`
attribute, and HTML attribute *values* genuinely are entity-decoded by
the browser as part of normal parsing — so an entity-encoded
`javascript:` scheme in that field decodes back into a real, clickable
`javascript:` URI. This mirrors a real, long-documented XSS filter
bypass class (entity-encoding a blocked URL scheme inside an href), as
opposed to the entity-in-body-text version, which looks similar but does
not work — a good one to let a team try and fail at once, then correct.

---

## Bonus Track — Four Independent Challenges

These four challenges are **separate from the main morning chain** (XSS →
CSRF → IDOR → BAC → SSRF → Path Traversal → LFI → RCE). They don't need to
be solved in order, and none of them depends on the others. Use them to:

- Give fast teams in **Session 6** a second track once they've traced the
  morning's incident — same investigation-pack capstone, more depth.
- Cover vulnerability classes the morning chain doesn't touch: SQL
  injection, mass assignment, insecure deserialization, and a business-logic
  race condition — all common in real bug bounty reports.
- Let you run a 2-track workshop format: "Track A" teams work the morning
  chain end-to-end while "Track B" teams (or the same teams, later) work
  the bonus track, then everyone compares notes at the close.

Each one has its own `VULN_*` flag (see the toggle table above) so you can
demo attack → flip the flag → demo the fix, exactly like the main chain.

### Bonus 1 — SQL Injection (invoice search)

**Entry point:** `/invoices/search?q=...` (also linked from the Invoices
page and the nav bar as "Search").

The search box is meant to filter your own invoices by description text.
The vulnerable query splices `q` directly into a SQL string instead of
using a parameter, so breaking out of the quoted `LIKE` clause lets you
`UNION` in rows from any other table — including `users`, which leaks
**every password hash in the system in one request**:

```
' UNION SELECT id, id, 1, username||':'||password, role, 0, created_at FROM users -- 
```

Column count and rough types have to line up with the `invoices` table
(7 columns), but the search page prints the raw row tuples straight back,
which is enough to read the result out. Crack the SHA-256 hashes offline
(no salt — a rainbow table or a fast GPU cracker makes short work of the
weak demo passwords) for a credential-based way back into any account,
including `superadmin`.

> **Hint tier 1:** "The search box looks like every other LIKE filter —
> except this is the only one in the app that isn't parameterized. Try a
> single quote first and see what breaks."
>
> **Hint tier 2:** "You need the exact same number of columns as the
> `invoices` table has. Count the table headers on the results page."

**Fix:** parameterized query (`?` placeholders) — SQL structure can never
be changed by user input, no matter what's inside `q`.

### Bonus 2 — Mass Assignment (JSON profile API)

**Entry point:** `POST /api/profile` (JSON body) — not linked anywhere in
the UI. Students have to notice it by watching Burp's proxy history while
using the normal "Edit Profile" page, or by reading the client-side JS.

The API is meant to let a (fictional) mobile app update `bio` and `email`.
It actually writes **every key in the posted JSON straight to the database
row**, with no field allowlist — including `role`:

```http
POST /api/profile HTTP/1.1
Host: localhost:5000
Cookie: session=<your session cookie>
Content-Type: application/json

{"bio": "hi", "role": "super-admin"}
```

One request, and a brand-new `user`-role account is now `super-admin` —
no need to ever touch the BAC-flagged `/admin/settings/promote-user`
route at all. This is the attack class behind several real-world
mass-assignment bugs (Rails `attr_accessible`-era CVEs, API frameworks
that auto-bind request bodies to ORM models).

> **Hint:** "The edit-profile *page* only sends `bio`. Is there another
> endpoint the *app* uses that takes more fields than the form shows?"

**Fix:** an explicit field allowlist (`bio`, `email` only) — privileged
fields are never even considered, regardless of what the client sends.

### Bonus 3 — Insecure Deserialization → RCE #2 (restore backup)

**Entry point:** `/admin/restore-backup`, super-admin only — reachable
either by legitimately being `superadmin`, or by chaining in from an
earlier privilege-escalation bug (BAC or the mass-assignment bug above).

This is a **second, fully independent path to remote code execution**,
parallel to the log-poisoning LFI chain from Session 4. It's a "legacy
settings importer" that still accepts the old pre-JSON backup format: a
base64-encoded Python pickle. `pickle.loads()` runs arbitrary code the
instant a crafted object is deserialized — no further action needed.

Attacker-side payload (run **locally**, never inside the lab container):

```python
import pickle, base64, os

class P:
    def __reduce__(self):
        return (os.system, ("id > /tmp/pwned_restore",))

print(base64.b64encode(pickle.dumps(P())).decode())
```

Paste the printed string into the "Restore Settings Backup" form. Check
`/tmp/pwned_restore` inside the backend container to confirm.

> **Hint:** "`pickle` and `json` can both represent a simple key/value
> object — but only one of them can also represent 'run this Python
> object's `__reduce__` method.' Which one does this form claim to accept?"

**Fix:** backups are restored from JSON only; `pickle` is never called on
request data under any code path.

### Bonus 4 — Race Condition (discount double-redemption)

**Entry point:** `POST /invoice/<id>/redeem` (form on the My Invoices page
— "Apply a discount code"). Seeded code: `WELCOME10` (10% off, intended
for **one single use across the whole system**).

This is a classic check-then-act (TOCTOU) bug, the same bug class behind
real-world gift-card and coupon-abuse incidents: the code's remaining
uses are read, checked in Python, and only written back afterward —
three separate round-trips with a window in between. Fire a burst of
concurrent requests at the same invoice (Burp Intruder with a
"null payloads" attack type and a high thread count is the easiest way
in the classroom; a 15–20 request Python `threading` or `asyncio` script
also works) and several of them land inside that window before any of
them commits — the single-use code gets redeemed far more than once,
and an invoice can be discounted well below what one legitimate 10%-off
redemption should produce.

> **Hint:** "The code says `max_uses = 1`. If twenty requests all check
> 'is this still under the limit?' at almost the same instant, how many
> of them can see 'yes' before any of them has written anything back?"

**Fix:** the check and the increment happen in **one atomic SQL
statement** (`UPDATE discount_codes SET uses=uses+1 WHERE code=? AND
uses < max_uses`) — SQLite's row-level write lock means only one
concurrent request can ever win, and the others see `rowcount == 0`.

### Bonus Track — Quick Reference

| # | Challenge | Entry point | Flag | Role needed |
|---|-----------|-------------|------|--------------|
| 1 | SQL Injection | `GET /invoices/search?q=` | `VULN_SQLI` | any user |
| 2 | Mass Assignment | `POST /api/profile` | `VULN_MASS_ASSIGN` | any user |
| 3 | Insecure Deserialization (RCE #2) | `POST /admin/restore-backup` | `VULN_DESERIALIZATION` | super-admin (chain in via #2 or BAC) |
| 4 | Race Condition | `POST /invoice/<id>/redeem` | `VULN_RACE` | any user, own invoice |

Also worth a mention while students are in Burp anyway: the post-login
`?next=` redirect (`/login?next=https://evil.example`) is **also**
unconditionally followed (`VULN_OPEN_REDIRECT`), which is exactly the kind
of link a phishing email would use to send a freshly-authenticated victim
straight to a credential-harvesting page. No separate "stage" needed —
just flag it as a one-liner while covering phishing in Session 1 or 4.

---

## Architecture

```
shadowcorp/
├── docker-compose.yml         ← One-command lab startup
├── csrf_demo.html             ← Attacker-controlled CSRF page
│
├── backend/                   ← Flask application (Python 3.11)
│   ├── app.py                 ← App factory, request logging middleware
│   ├── config.py              ← Vulnerability toggle flags
│   ├── auth.py                ← Password hashing, session, decorators
│   ├── db.py                  ← SQLite helpers
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── routes/
│   │   ├── auth_routes.py     ← /login /register /logout
│   │   ├── profile_routes.py  ← /dashboard /profile /profile/edit  [XSS, CSRF]
│   │   ├── invoice_routes.py  ← /invoices /invoice/<id> /user/<id>  [IDOR]
│   │   ├── admin_routes.py    ← /admin/* [BAC, JWT, CSRF]
│   │   ├── webhook_routes.py  ← /admin/webhook-test /admin/import-logo [SSRF]
│   │   ├── document_routes.py ← /documents/view [Path Traversal]
│   │   ├── page_routes.py     ← /pages/render [LFI, RCE]
│   │   ├── upload_routes.py   ← /admin/upload-report [File Upload RCE chain]
│   │   └── extra_routes.py    ← Bonus track: /invoices/search [SQLi],
│   │                             /api/profile [Mass Assignment],
│   │                             /admin/restore-backup [Deserialization → RCE #2],
│   │                             /invoice/<id>/redeem [Race Condition]
│   ├── templates/             ← Jinja2 HTML templates
│   ├── static/css/main.css    ← Dark corporate stylesheet
│   ├── static/js/main.js      ← Minimal frontend JS
│   ├── documents/             ← Allowed documents directory
│   ├── pages/                 ← Safe pages directory
│   ├── uploads/               ← Uploaded incident reports (RCE stage)
│   └── logs/access.log        ← Request log (sanitized)
│
├── internal-api/              ← Node.js internal microservice (SSRF target)
│   ├── server.js              ← Express app with /admin/secret endpoint
│   ├── package.json
│   └── Dockerfile             ← NO host port exposed
│
└── seed/
    └── seed.py                ← Database seeder (7 users, invoices, audit log)
```

**Network topology:**
```
[Student Browser] → localhost:5000 → [backend container]
                                            ↓ (Docker internal network)
                                     [internal-api:3000]  ← never reachable directly
```

---

*Shadow Corp Lab — built for educational demonstration of OWASP Top 10 vulnerabilities.*  
*All attack paths are intentional and fully documented in the source code.*
