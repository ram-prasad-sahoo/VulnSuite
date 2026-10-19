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
- [📋 Prerequisites & System Requirements](#-prerequisites--system-requirements)
- [📥 Step-by-Step Installation](#-step-by-step-installation)
  - [Step 1: Clone the Repository](#step-1-clone-the-repository)
  - [Method 1: Automated One-Click Startup (Recommended)](#method-1-automated-one-click-startup-recommended)
  - [Method 2: Manual Docker Compose](#method-2-manual-docker-compose)
  - [Method 3: Manual Native Setup (Without Docker)](#method-3-manual-native-setup-without-docker)
- [🎮 How to Use & Explore the Lab](#-how-to-use--explore-the-lab)
  - [1. Access the Application](#1-access-the-application)
  - [2. Sign In with Role-Based Accounts](#2-sign-in-with-role-based-accounts)
  - [3. Step-by-Step Testing & Exploration Workflow](#3-step-by-step-testing--exploration-workflow)
  - [4. How to Update the Lab](#4-how-to-update-the-lab)
  - [5. How to Reset the Lab Environment](#5-how-to-reset-the-lab-environment)
  - [6. How to Stop the Lab](#6-how-to-stop-the-lab)
  - [7. Instructors & Trainers: Live Patch Demonstration](#7-instructors--trainers-live-patch-demonstration)
- [🎛️ Vulnerability Flags & Patch Simulation](#-vulnerability-flags--patch-simulation)
- [📁 Repository Structure](#-repository-structure)
- [👨‍💻 Author & Connect](#-author--connect)
- [⚠️ Disclaimer & Educational Use Notice](#️-disclaimer--educational-use-notice)

---

## 🏢 Overview & Business Logic

**VulnSuite** is an intentionally vulnerable web and API environment that models a modern multi-tier corporate operations platform. Unlike fragmented CTF micro-challenges, VulnSuite presents a unified, stateful application designed around cohesive business workflows:

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

## 📋 Prerequisites & System Requirements

Before installing VulnSuite, ensure your machine satisfies either **Option A (Docker - Recommended)** or **Option B (Native Local)**:

| Requirement | Option A: Docker (Easiest) | Option B: Native Setup |
|:---|:---|:---|
| **Operating System** | Windows 10/11, macOS, Linux | Windows 10/11, macOS, Linux |
| **Container Engine** | Docker Desktop 20+ & Docker Compose | Not required |
| **Python** | Not required (containerized) | Python 3.10, 3.11, or 3.12 |
| **Node.js** | Not required (containerized) | Node.js 18+ & npm (for internal API) |
| **Git** | Git 2.30+ | Git 2.30+ |
| **Available Ports** | `9999` (Web Portal), `3000` (Internal API) | `9999` (Web Portal), `3000` (Internal API) |

---

## 📥 Step-by-Step Installation

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the VulnSuite repository:

```bash
git clone https://github.com/ram-prasad-sahoo/VulnSuite.git
cd VulnSuite
```

---

### Method 1: Automated One-Click Startup (Recommended)

VulnSuite includes intelligent launcher scripts that **automatically detect your system, check GitHub for updates, configure dependencies, and launch the lab**:

#### 🪟 On Windows:
Double-click `start_lab.bat` in File Explorer, or run in Command Prompt / PowerShell:
```cmd
start_lab.bat
```

#### 🐧 On Linux:
Make the script executable and launch:
```bash
chmod +x start_lab.sh
./start_lab.sh
```

#### 🍎 On macOS:
Make the script executable and launch in Terminal:
```bash
chmod +x start_lab.sh
./start_lab.sh
```

> **What the Launcher Does Automatically:**
> 1. **Checks for Updates**: Queries GitHub to see if a newer version of VulnSuite exists. If an update is found, it prompts you `(y/n)` to update with one keystroke.
> 2. **Auto-Detects Docker**: If Docker Desktop is running, it builds the containers and starts the lab in full container isolation.
> 3. **Auto-Detects Native Python**: If Docker is not running, it automatically creates a `.venv` virtual environment, installs all required packages (`pip install -r backend/requirements.txt`), configures Node.js for the internal microservice, and seeds the SQLite database.
> 4. **Auto-Opens Browser**: Launches `http://localhost:9999` in your default web browser automatically.

---

### Method 2: Manual Docker Compose

If you prefer executing standard Docker commands directly:

```bash
# 1. Build and start the containers in the foreground
docker-compose up --build

# Or run in detached (background) mode:
docker-compose up --build -d
```

* **Web Portal URL**: [http://localhost:9999](http://localhost:9999)
* **Internal API Microservice**: Runs inside Docker network at `http://internal-api:3000` (isolated from external host)

To view live container logs:
```bash
docker-compose logs -f
```

To stop the containers:
```bash
docker-compose down
```

---

### Method 3: Manual Native Setup (Without Docker)

If you do not have Docker Desktop installed, you can run VulnSuite directly on your host machine:

#### 1. Set Up Python Virtual Environment
* **On Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r backend/requirements.txt
  ```

* **On Windows (Command Prompt / PowerShell)**:
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r backend\requirements.txt
  ```

#### 2. Initialize and Seed the Database
```bash
# On Linux / macOS:
DATABASE="backend/LabDatabase.db" python seed/seed.py

# On Windows:
set DATABASE=backend\LabDatabase.db
python seed\seed.py
```

#### 3. Start the Internal Node.js API Service (Optional but Recommended)
In a separate terminal:
```bash
cd internal-api
npm install
node server.js
```

#### 4. Launch the VulnSuite Web Portal
In your primary activated terminal:
```bash
# On Linux / macOS:
export PORT=9999
export DATABASE="backend/LabDatabase.db"
python backend/app.py

# On Windows:
set PORT=9999
set DATABASE=backend\LabDatabase.db
python backend\app.py
```

Navigate to [http://localhost:9999](http://localhost:9999) in your web browser.

---

## 🎮 How to Use & Explore the Lab

### 1. Access the Application
Once the application is running, open your browser and navigate to:
```
http://localhost:9999
```

### 2. Sign In with Role-Based Accounts
VulnSuite includes pre-configured accounts representing different organizational tiers. Use the credentials below to log in at [http://localhost:9999/login](http://localhost:9999/login):

| Persona | Username | Password | Role Tier | What You Can Access |
|:---|:---|:---|:---|:---|
| **Standard User** | `alice` | `Password123!` | `user` | Personal profile, invoices, redeem discount credits, view documents |
| **Support Operator** | `support_admin` | `Admin@Shadow1` | `support-admin` | User directory, support settings, email modifications, basic admin console |
| **System Admin** | `superadmin` | `Super@Shadow1` | `super-admin` | Full system governance, role promotion, webhook tester, backup restoration, incident uploads |

---

### 3. Step-by-Step Testing & Exploration Workflow

#### Phase 1: Reconnaissance & Account Exploration
* Log in as `alice` (`Password123!`).
* Inspect your active session cookies, headers, and UI layout.
* Navigate between **Invoices**, **Profile**, and **Documents** to map the application attack surface.

#### Phase 2: User Profile & Content Ingestion
* Navigate to **Edit Profile** (`/profile/edit`).
* Test how the platform handles user input in the **Bio** and **Website** fields.
* Save your changes and visit your public profile at `/profile/alice` to observe how data is parsed and displayed.

#### Phase 3: Financial Invoices & Access Controls
* Click on **Invoices** in the top navigation bar.
* Open an invoice and observe the URL format (`/invoice/1`).
* Test whether users can access records belonging to other employees by modifying the identifier.
* Use the **Search Invoices** bar (`/invoices/search`) to search transaction descriptions and test query input handling.
* Open a pending invoice and test the **Promotional Credit Redemption** (`/invoice/<id>/redeem`) with promo code `WELCOME10`.

#### Phase 4: Document Repository & Dynamic Templates
* Visit **Documents** (`/documents/view?doc=acceptable_use_policy.txt`).
* Inspect how file paths are accepted and loaded by the backend server.
* Visit the dynamic page engine (`/pages/render?page=about`) and examine how system templates are rendered.

#### Phase 5: Administrative Control & API Services
* Log out and log in as `support_admin` or `superadmin`.
* Access the **Admin Dashboard** (`/admin/dashboard`):
  * **Role Promotion Console** (`/admin/settings/promote-user`): Observe access control validation on administrative actions.
  * **Webhook Integration Tester** (`/admin/webhook-test`): Test outbound network requests and interactions with the internal API.
  * **Incident Report Ingestion** (`/admin/upload-report`): Evaluate file upload restrictions and server-side template processing.
  * **API Token Inspection** (`/admin/api/token`): Analyze JWT token creation and validation mechanics.
  * **Backup & Restore Utility** (`/admin/restore-backup`): Analyze how system restore archives and serialized payloads are handled.

---

### 4. How to Update the Lab

VulnSuite includes an automatic update checking mechanism:
* **Using Launcher**: Run `start_lab.bat` or `./start_lab.sh`. If updates exist on GitHub, simply type `y` when prompted.
* **Manual Git Update**:
  ```bash
  git pull origin main
  ```

---

### 5. How to Reset the Lab Environment

If test payloads, modified profiles, or uploaded files clutter your database, reset the environment back to fresh defaults at any time:

* **If running with Docker**:
  ```bash
  docker-compose down -v
  docker-compose up --build
  ```

* **If running natively with Python**:
  ```bash
  # Linux / macOS:
  DATABASE="backend/LabDatabase.db" python seed/seed.py

  # Windows:
  set DATABASE=backend\LabDatabase.db
  python seed\seed.py
  ```

---

### 6. How to Stop the Lab

* **Docker Mode**: Press `Ctrl + C` in the running terminal, or run `docker-compose down`.
* **Native Mode**: Press `Ctrl + C` in the terminal windows running Python and Node.js.

---

### 7. Instructors & Trainers: Live Patch Demonstration

Demonstrate the difference between **vulnerable** and **remediated (secure)** code in real-time without modifying code files by passing environment toggle flags:

```bash
# Example 1: Run with Stored XSS and CSRF patched (secure mode):
VULN_XSS=false VULN_CSRF=false docker-compose up

# Example 2: Run with IDOR and SQL Injection patched (secure mode):
VULN_IDOR=false VULN_SQLI=false docker-compose up
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

---

## 📁 Repository Structure

```
VulnSuite/
├── docker-compose.yml          # Container configuration and network bridge
├── logo.svg                    # Vector graphic identity
├── start_lab.bat               # Windows automation launcher (auto-install & auto-update)
├── start_lab.sh                # Linux & macOS automation launcher (auto-install & auto-update)
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

## ⚠️ Disclaimer & Educational Use Notice

> **VulnSuite is designed strictly for authorized educational research, training, and vulnerability assessment demonstrations. Never deploy this application on a public or untrusted network.**

<p align="center">
  <sub>VulnSuite v1.0 © 2026. Built for cybersecurity education, research, and security benchmarking.</sub>
</p>
