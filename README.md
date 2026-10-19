<p align="center">
  <img src="logo.svg" alt="VulnSuite Logo" width="120" height="120" />
</p>

<h1 align="center">VulnSuite</h1>
<p align="center">
  <b>A Deliberately Vulnerable Web & API Security Lab</b>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/ramprasadsahoo/"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Connect" /></a>
  <img src="https://img.shields.io/badge/Version-1.0-blue?style=for-the-badge" alt="Version 1.0" />
  <img src="https://img.shields.io/badge/License-Educational-brightgreen?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

---

## 🏢 Platform & Business Logic Overview

**VulnSuite** simulates a multi-tier Corporate Operations and ERP portal used by internal employees, billing departments, and platform administrators.

```
┌────────────────────────────────────────────────────────────────────────┐
│                             VulnSuite v1.0                             │
├───────────────────┬──────────────────────┬─────────────────────────────┤
│ User Management   │ Financial & Invoices │ Document & Knowledge Base   │
│ • Staff Directory │ • Client Billing     │ • Incident Report Uploads   │
│ • Profiles & Bios │ • Discount Redemptions│ • Internal Notices & Docs  │
│ • Role Hierarchy  │ • Invoice Search     │ • Dynamic Page Templates    │
└───────────────────┴──────────────────────┴─────────────────────────────┘
                                  │
                                  ▼ (Internal Isolated Network)
                    ┌───────────────────────────┐
                    │  Internal Admin Services  │
                    │  (Port 3000 — Restricted) │
                    └───────────────────────────┘
```

The portal provides distinct operational interfaces:
* **User Workspace**: Profile customizations, billing receipts, team directories, and document viewing.
* **Financial Management**: Real-time invoice review, promo/discount application, and parameterized ledger searching.
* **Administrative Console**: Role delegation, system audit logs, internal webhook configurations, incident report archives, and backup restorations.
* **Internal Microservice (`internal-api`)**: An isolated backend service managing environment configurations and infrastructure keys.

---

## 🎯 Vulnerability Surface

VulnSuite incorporates realistic security vulnerabilities spanning modern web applications, RESTful APIs, and backend architectures:

### 🌐 Web Application Vulnerabilities

| # | Vulnerability Category | OWASP Top 10 | Target Surface / Feature |
|---|------------------------|--------------|--------------------------|
| 1 | **Stored Cross-Site Scripting (XSS)** | A03:2021 – Injection | Profile Management (`/profile/edit`, `/profile/<username>`) |
| 2 | **Cross-Site Request Forgery (CSRF)** | A01:2021 – Broken Access Control | Administrative State Changes (`/admin/change-email`) |
| 3 | **Insecure Direct Object Reference (IDOR)** | A01:2021 – Broken Access Control | Billing & Account Ledgers (`/invoice/<id>`, `/user/<id>`) |
| 4 | **Broken Access Control & Privilege Escalation** | A01:2021 – Broken Access Control | Role Promotion Console (`/admin/settings/promote-user`) |
| 5 | **SQL Injection (SQLi)** | A03:2021 – Injection | Financial Ledger Search (`/invoices/search`) |
| 6 | **Path Traversal (Arbitrary File Read)** | A01:2021 – Broken Access Control | Document Repository Viewer (`/documents/view`) |
| 7 | **Local File Inclusion (LFI)** | A01:2021 – Broken Access Control | Dynamic Page Renderer (`/pages/render`) |
| 8 | **Remote Code Execution (RCE via File Upload)** | A03:2021 – Injection | Incident Report Ingestion (`/admin/upload-report`) |
| 9 | **Race Condition (Concurrency Flaw)** | A04:2021 – Insecure Design | Discount & Credit Redemption (`/invoice/<id>/redeem`) |
| 10 | **Open Redirect** | A01:2021 – Broken Access Control | Authentication Redirection Handler (`/login?next=`) |

---

### 🔌 API & Authentication Vulnerabilities

| # | Vulnerability Category | OWASP API Security | Target Surface / Feature |
|---|------------------------|--------------------|--------------------------|
| 11 | **Mass Assignment** | API3:2023 – Broken Object Property Level Authorization | REST Profile Endpoint (`POST /api/profile`) |
| 12 | **Insecure JWT Token Verification** | API2:2023 – Broken Authentication | Token Authentication Handlers (`/admin/api/token`) |
| 13 | **Server-Side Request Forgery (SSRF)** | API7:2023 – Server-Side Request Forgery | Webhook Testing & Asset Importer (`/admin/webhook-test`) |
| 14 | **Insecure Deserialization (RCE)** | A08:2021 – Software & Data Integrity Failures | System Archive Restore (`/admin/restore-backup`) |

---

## 🔑 Lab Credentials

The test environment includes pre-configured user accounts covering multiple permission tiers:

| Username | Password | Role / Permission Tier | Notes |
|:---|:---|:---|:---|
| `alice` | `Password123!` | `user` | Product Team |
| `bob` | `Password123!` | `user` | Engineering Lead |
| `carol` | `Password123!` | `user` | Finance Analyst |
| `dave` | `Password123!` | `user` | Sales Lead |
| `eve` | `Password123!` | `user` | New Onboarding |
| `support_admin` | `Admin@Shadow1` | `support-admin` | Support Tier Administration |
| `superadmin` | `Super@Shadow1` | `super-admin` | Full System Authority |

---

## 🚀 Quick Start

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Docker Compose v2+)

### Running the Lab with Docker

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR_GITHUB_USERNAME>/VulnSuite.git
cd VulnSuite

# 2. Build and start services
docker-compose up --build
```

The application will be accessible at:
* **Web Portal**: [http://localhost:9999](http://localhost:9999)
* **Internal API**: `http://internal-api:3000` *(Internal network only — not exposed to host)*

To stop the environment and reset the database:
```bash
docker-compose down -v
```

---

## 🎛️ Vulnerability Configuration Flags

VulnSuite includes environment toggles allowing instructors, evaluators, and auditors to dynamically enable or disable vulnerabilities to demonstrate patched behavior:

| Environment Variable | Default | Feature Controlled |
|:---|:---:|:---|
| `VULN_XSS` | `true` | Enables raw HTML rendering vs. context-aware sanitization |
| `WAF_ENABLED` | `true` | Enables perimeter input filter ("WAF-lite") |
| `VULN_CSRF` | `true` | Disables anti-CSRF token verification |
| `VULN_IDOR` | `true` | Omits user-ownership validation on invoice records |
| `VULN_BAC` | `true` | Allows non-superadmin users to access elevation routes |
| `VULN_JWT` | `true` | Disables cryptographic signature verification on JWTs |
| `VULN_SSRF` | `true` | Allows outbound HTTP requests without IP/domain allowlists |
| `VULN_PATH_TRAVERSAL` | `true` | Disables directory path resolution restrictions |
| `VULN_LFI` | `true` | Allows arbitrary file loading in the page rendering engine |
| `VULN_RCE` | `true` | Processes included templates with dynamic code execution |
| `VULN_SQLI` | `true` | Uses string-concatenated SQL queries in search |
| `VULN_MASS_ASSIGN` | `true` | Directly binds JSON parameters to database record fields |
| `VULN_DESERIALIZATION`| `true` | Deserializes untrusted object streams on backup restore |
| `VULN_RACE` | `true` | Exposes non-atomic balance updates during redemptions |
| `VULN_OPEN_REDIRECT` | `true` | Follows arbitrary redirect destinations after authentication |

---

## 🏗️ Architecture

```
VulnSuite/
├── docker-compose.yml          # Container orchestration & network bridge
├── logo.svg                    # VulnSuite SVG branding
├── start_lab.bat               # Windows one-click startup automation
│
├── backend/                    # Python / Flask Application
│   ├── app.py                  # Core application setup & middleware
│   ├── config.py               # Vulnerability flag configurations
│   ├── auth.py                 # Authentication and role decorators
│   ├── db.py                   # Database connection handling
│   ├── waf.py                  # Perimeter content filter implementation
│   ├── routes/                 # Endpoint modular controllers
│   ├── static/                 # Stylesheets, scripts, and SVG assets
│   ├── templates/              # Jinja2 presentation templates
│   ├── documents/              # Public / shared document storage
│   ├── pages/                  # Static renderable views
│   └── uploads/                # Incident report storage directory
│
├── internal-api/               # Node.js Internal Microservice
│   ├── server.js               # Mock configuration and metadata service
│   └── package.json
│
└── seed/
    └── seed.py                 # Database initialization & mock data seeder
```

---

## 👨‍💻 Connect & Feedback

Crafted by **Ramprasad Sahoo**. Connect on LinkedIn for discussions, feedback, or security collaboration:

<p align="left">
  <a href="https://www.linkedin.com/in/ramprasadsahoo/">
    <img src="https://img.shields.io/badge/LinkedIn-Ramprasad%20Sahoo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="Ramprasad Sahoo LinkedIn" />
  </a>
</p>

---

> ⚠️ **DISCLAIMER & EDUCATIONAL USE NOTICE**  
> **VulnSuite** is designed strictly for authorized educational research, training, and vulnerability assessment demonstrations. Never deploy this application on a public or untrusted network.

<p align="center">
  <sub>VulnSuite v1.0 © 2026. Built for cybersecurity education, research, and security benchmarking.</sub>
</p>
