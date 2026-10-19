<p align="center">
  <img src="logo.svg" alt="VulnSuite Logo" width="130" height="130" />
</p>

<h1 align="center">VulnSuite</h1>
<p align="center">
  <b>A Comprehensive, Deliberately Vulnerable Web & API Security Assessment Lab</b>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/ramprasadsahoo/"><img src="https://img.shields.io/badge/LinkedIn-Ramprasad%20Sahoo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Connect" /></a>
  <img src="https://img.shields.io/badge/Version-1.0-blue?style=for-the-badge" alt="Version 1.0" />
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Node.js-18-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready" />
  <img src="https://img.shields.io/badge/OWASP-Top%2010%20Covered-red?style=for-the-badge" alt="OWASP Top 10" />
</p>

---

## 📑 Table of Contents

- [Overview & Business Logic](#-overview--business-logic)
- [Target Audiences & Use Cases](#-target-audiences--use-cases)
- [Architecture & Network Topology](#-architecture--network-topology)
- [Vulnerability Matrix](#-vulnerability-matrix)
  - [Web Application Security](#-web-application-security)
  - [API & Authentication Security](#-api--authentication-security)
- [Pre-configured Lab Credentials](#-pre-configured-lab-credentials)
- [Quick Start Guide](#-quick-start-guide)
  - [Option A: One-Click Startup (Windows)](#option-a-one-click-startup-windows)
  - [Option B: Docker Compose (Cross-Platform)](#option-b-docker-compose-cross-platform)
  - [Option C: Manual / Native Local Run](#option-c-manual--native-local-run)
- [Vulnerability Flags & Patch Simulation](#-vulnerability-flags--patch-simulation)
- [Repository Structure](#-repository-structure)
- [Author & Connect](#-author--connect)
- [Disclaimer & Educational Notice](#-disclaimer--educational-notice)

---

## 🏢 Overview & Business Logic

**VulnSuite** is an intentionally vulnerable web and API environment that models a modern multi-tier corporate management platform. Unlike fragmented CTF micro-challenges, VulnSuite presents a unified, stateful application designed around cohesive business workflows:

```
┌────────────────────────────────────────────────────────────────────────┐
│                             VulnSuite v1.0                             │
├───────────────────┬──────────────────────┬─────────────────────────────┤
│ User Management   │ Financial Ledgers    │ Knowledge Repository        │
│ • Staff Directory │ • Invoicing & Status │ • Incident Report Archive   │
│ • Profile Custom  │ • Discount Credits   │ • Internal System Notices   │
│ • Tiered RBAC     │ • Ledger Search      │ • Dynamic Page Templates    │
└───────────────────┴──────────────────────┴─────────────────────────────┘
                                  │
                                  ▼ (Isolated Docker Bridge Network)
                    ┌───────────────────────────┐
                    │  Internal Admin Services  │
                    │  (Port 3000 — Restricted) │
                    └───────────────────────────┘
```

### Key Business Domains:
1. **User Identity & Role Hierarchy**: Multi-tier access control containing standard users (`user`), operational support staff (`support-admin`), and system administrators (`super-admin`).
2. **Financial Operations**: User-specific billing ledgers, promotional credit redemptions, and searchable invoice indexes.
3. **Corporate Documentation**: Operational policy viewers, public announcements, and administrative incident report ingest engines.
4. **Internal Microservices**: An isolated backend service simulating an unexposed internal microservice hosting cloud credentials and internal tokens.

---

## 🎯 Target Audiences & Use Cases

* **Penetration Testers & AppSec Engineers**: Practice identifying modern web and API vulnerability classes within a realistic application architecture.
* **Security Trainers & Educators**: Demonstrate live exploit-and-remediate workflows using atomic environment configuration flags.
* **Red / Blue Teams**: Validate web application firewall (WAF) rule sets, monitor logs for exploit signatures, and test detection rules.
* **Security Scanner Benchmarking**: Evaluate vulnerability scanners (Burp Suite, OWASP ZAP, Caido, sqlmap, Nuclei) against complex multi-step application logic.

---

## 🏗️ Architecture & Network Topology

VulnSuite runs on an isolated network topology to simulate corporate DMZs and internal service boundaries:

```
                  ┌────────────────────────────────────────┐
                  │          Auditor / Browser             │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼ (Port 9999)
                  ┌────────────────────────────────────────┐
                  │       VulnSuite Web Application        │
                  │             (Python/Flask)             │
                  │   • Authentication & Session Storage   │
                  │   • Invoicing & File Ingestion         │
                  │   • SQLite Database (LabDatabase.db)   │
                  └───────────────────┬────────────────────┘
                                      │
                         (Internal Docker Network ONLY)
                         (No External Host Exposure)
                                      │
                                      ▼ (Port 3000)
                  ┌────────────────────────────────────────┐
                  │        Internal Administration API     │
                  │             (Node.js/Express)          │
                  │   • Internal System Configuration      │
                  │   • Simulated Cloud Metadata & Keys    │
                  └────────────────────────────────────────┘
```

---

## 🎯 Vulnerability Matrix

The platform incorporates comprehensive security vulnerabilities spanning both the **OWASP Top 10** and the **OWASP API Security Top 10**:

### 🌐 Web Application Security

| # | Vulnerability | CWE | OWASP Top 10 | Target Surface | Minimum Role |
|:---:|:---|:---:|:---:|:---|:---:|
| **01** | **Stored Cross-Site Scripting (XSS)** | CWE-79 | A03:2021 – Injection | `/profile/edit` & `/profile/<username>` | `user` |
| **02** | **Cross-Site Request Forgery (CSRF)** | CWE-352 | A01:2021 – Broken Access Control | `/admin/change-email` | `support-admin` |
| **03** | **Insecure Direct Object Reference (IDOR)** | CWE-639 | A01:2021 – Broken Access Control | `/invoice/<id>` & `/user/<id>` | `user` |
| **04** | **Broken Access Control & Privilege Escalation** | CWE-269 | A01:2021 – Broken Access Control | `/admin/settings/promote-user` | `support-admin` |
| **05** | **SQL Injection (SQLi)** | CWE-89 | A03:2021 – Injection | `/invoices/search` | `user` |
| **06** | **Path Traversal (Arbitrary File Read)** | CWE-22 | A01:2021 – Broken Access Control | `/documents/view` | `user` |
| **07** | **Local File Inclusion (LFI)** | CWE-98 | A01:2021 – Broken Access Control | `/pages/render` | `user` |
| **08** | **Remote Code Execution (RCE via File Upload)** | CWE-434 | A03:2021 – Injection | `/admin/upload-report` | `support-admin` |
| **09** | **Race Condition (Concurrency Flaw)** | CWE-362 | A04:2021 – Insecure Design | `/invoice/<id>/redeem` | `user` |
| **10** | **Open Redirect** | CWE-601 | A01:2021 – Broken Access Control | `/login?next=` | Unauthenticated |

---

### 🔌 API & Authentication Security

| # | Vulnerability | CWE | OWASP API Security | Target Surface | Minimum Role |
|:---:|:---|:---:|:---:|:---|:---:|
| **11** | **Mass Assignment** | CWE-915 | API3:2023 – Broken Object Property Level Auth | `POST /api/profile` | `user` |
| **12** | **Insecure JWT Signature Verification** | CWE-347 | API2:2023 – Broken Authentication | `/admin/api/token` | `support-admin` |
| **13** | **Server-Side Request Forgery (SSRF)** | CWE-918 | API7:2023 – Server-Side Request Forgery | `/admin/webhook-test` | `support-admin` |
| **14** | **Insecure Deserialization (RCE)** | CWE-502 | A08:2021 – Software & Data Integrity | `/admin/restore-backup` | `super-admin` |

---

## 🔑 Pre-configured Lab Credentials

The seed script creates the following user accounts:

| Username | Password | Email Address | Role Tier | Account Scope |
|:---|:---|:---|:---|:---|
| `alice` | `Password123!` | `alice@vulnsuite.com` | `user` | Product Team |
| `bob` | `Password123!` | `bob@vulnsuite.com` | `user` | Engineering Lead |
| `carol` | `Password123!` | `carol@vulnsuite.com` | `user` | Finance Analyst |
| `dave` | `Password123!` | `dave@vulnsuite.com` | `user` | Sales Lead |
| `eve` | `Password123!` | `eve@vulnsuite.com` | `user` | New Onboarding |
| `support_admin` | `Admin@Shadow1` | `support@vulnsuite.com` | `support-admin` | Operational Support Console |
| `superadmin` | `Super@Shadow1` | `admin@vulnsuite.com` | `super-admin` | Full System Authority |

---

## 🚀 Quick Start Guide

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Docker Compose v2+) or Python 3.11+

### Option A: One-Click Startup Scripts

* **Windows**: Double-click `start_lab.bat` or execute in PowerShell:
  ```powershell
  .\start_lab.bat
  ```

* **Linux & macOS**: Make executable and run in your terminal:
  ```bash
  chmod +x start_lab.sh
  ./start_lab.sh
  ```

These scripts verify that Docker daemon is running, build and initialize the container stack, and automatically open `http://localhost:9999` in your default browser.

---

### Option B: Docker Compose (Cross-Platform)

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR_GITHUB_USERNAME>/VulnSuite.git
cd VulnSuite

# 2. Build and launch the environment
docker-compose up --build
```

Access Points:
* **Web Portal**: [http://localhost:9999](http://localhost:9999)
* **Internal API**: `http://internal-api:3000` *(Reachable internally through server-side requests)*

To stop the lab and reset all state:
```bash
docker-compose down -v
```

---

### Option C: Manual / Native Local Run

If running outside Docker:

```bash
# 1. Setup Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Seed database
python ../seed/seed.py

# 3. Start web application
python app.py

# 4. In a separate terminal, launch the internal API service
cd ../internal-api
npm install
node server.js
```

---

## 🎛️ Vulnerability Flags & Patch Simulation

VulnSuite includes environment toggles allowing real-time demonstration of both **vulnerable** and **remediated** application behavior:

| Environment Variable | Default | Purpose / Remediation Mode |
|:---|:---:|:---|
| `VULN_XSS` | `true` | When `false`: Enforces HTML entity output escaping over `\|safe` |
| `WAF_ENABLED` | `true` | When `false`: Removes input blocklist content filter |
| `VULN_CSRF` | `true` | When `false`: Validates anti-CSRF synchronizer tokens on state changes |
| `VULN_IDOR` | `true` | When `false`: Validates user ownership on record lookups |
| `VULN_BAC` | `true` | When `false`: Restricts administrative routes to verified `super-admin` |
| `VULN_JWT` | `true` | When `false`: Requires and cryptographically validates JWT signatures |
| `VULN_SSRF` | `true` | When `false`: Enforces destination IP/domain allowlists |
| `VULN_PATH_TRAVERSAL` | `true` | When `false`: Restricts file reads to sandboxed canonical paths |
| `VULN_LFI` | `true` | When `false`: Validates page templates against strict allowlists |
| `VULN_RCE` | `true` | When `false`: Disables dynamic Jinja2 template execution on uploads |
| `VULN_SQLI` | `true` | When `false`: Executes parameterized queries |
| `VULN_MASS_ASSIGN` | `true` | When `false`: Whitelists permitted request properties |
| `VULN_DESERIALIZATION`| `true` | When `false`: Uses strict JSON parsers instead of native object unpicklers |
| `VULN_RACE` | `true` | When `false`: Executes balance operations within atomic transactions |
| `VULN_OPEN_REDIRECT` | `true` | When `false`: Validates redirect URLs against same-origin policies |

*Example: Running with XSS and CSRF patched:*
```bash
VULN_XSS=false VULN_CSRF=false docker-compose up
```

---

## 📁 Repository Structure

```
VulnSuite/
├── docker-compose.yml          # Container configuration and network bridge
├── logo.svg                    # Vector graphic identity
├── start_lab.bat               # Windows automation launcher
├── start_lab.sh                # Linux & macOS automation launcher
│
├── backend/                    # Core Flask Application
│   ├── app.py                  # Application factory and middleware
│   ├── config.py               # Vulnerability flag configurations
│   ├── auth.py                 # Session management and RBAC decorators
│   ├── db.py                   # SQLite connection helpers
│   ├── waf.py                  # Perimeter content filter implementation
│   ├── routes/                 # Modular endpoint controllers
│   ├── static/                 # Stylesheets, scripts, and SVG assets
│   ├── templates/              # Jinja2 layout templates
│   ├── documents/              # Public repository files
│   ├── pages/                  # Static render views
│   └── uploads/                # Incident report storage
│
├── internal-api/               # Node.js Internal Microservice
│   ├── server.js               # Metadata & configuration API
│   ├── package.json
│   └── Dockerfile
│
└── seed/
    └── seed.py                 # Database initialization & mock data seeder
```

---

## 👨‍💻 Author & Connect

Developed by **Ramprasad Sahoo**.

Feel free to connect on LinkedIn for discussions, feedback, or collaborations:

<p align="left">
  <a href="https://www.linkedin.com/in/ramprasadsahoo/">
    <img src="https://img.shields.io/badge/LinkedIn-Ramprasad%20Sahoo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="Ramprasad Sahoo LinkedIn" />
  </a>
</p>

---

> ⚠️ **DISCLAIMER & EDUCATIONAL NOTICE**  
> **VulnSuite** is created strictly for educational purposes, authorized security testing, and defensive training. Never deploy this software to production environments or publicly accessible networks. Unauthorized testing of systems without prior mutual consent is strictly illegal.

<p align="center">
  <sub>VulnSuite v1.0 © 2026. Built for cybersecurity education, research, and security benchmarking.</sub>
</p>
