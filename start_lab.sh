#!/usr/bin/env bash
# ===================================================
#             VulnSuite Lab Startup
#           (Linux & macOS Quick Start)
# ===================================================

set -e

# Detect operating system
OS="$(uname -s)"

echo "==================================================="
echo "              VulnSuite Lab Startup                "
echo "==================================================="
echo ""

URL="http://localhost:9999"

# Helper function to open browser
open_browser() {
    echo "[*] Opening browser ($URL)..."
    if [ "$OS" = "Darwin" ]; then
        open "$URL" >/dev/null 2>&1 || true
    elif [ "$OS" = "Linux" ]; then
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$URL" >/dev/null 2>&1 || true
        elif command -v sensible-browser >/dev/null 2>&1; then
            sensible-browser "$URL" >/dev/null 2>&1 || true
        fi
    fi
}

# ── 0. Automatic Update Check from GitHub ────────────
if command -v git >/dev/null 2>&1 && [ -d ".git" ]; then
    if git remote get-url origin >/dev/null 2>&1; then
        echo "[*] Checking for updates from GitHub..."
        if git fetch origin --quiet 2>/dev/null; then
            LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "")
            REMOTE_COMMIT=$(git rev-parse @{u} 2>/dev/null || echo "")

            if [ -n "$REMOTE_COMMIT" ] && [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
                echo ""
                echo "==================================================="
                echo "  [!] A new version of VulnSuite is available!     "
                echo "==================================================="
                read -p "  Do you want to download and update now? (y/n): " UPDATE_CHOICE
                case "$UPDATE_CHOICE" in
                    y|Y )
                        echo "[*] Downloading latest updates from GitHub..."
                        git pull --quiet
                        echo "[+] Updated successfully to the latest version!"
                        echo ""
                        ;;
                    * )
                        echo "[*] Skipping update. Continuing with installed version..."
                        echo ""
                        ;;
                esac
            else
                echo "[+] VulnSuite is up to date."
            fi
        else
            echo "[*] Offline or cannot connect to GitHub. Continuing with local version..."
        fi
    fi
fi

# ── 1. Check if Docker is available and running ──────
USE_DOCKER=false

if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        USE_DOCKER=true
    fi
fi

if [ "$USE_DOCKER" = true ]; then
    echo "[+] Docker detected and running!"
    echo "[*] Automatically building environment and installing dependencies via Docker..."

    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    fi

    $COMPOSE_CMD up --build -d
    echo "[*] Waiting for web application to initialize..."
    sleep 6
    open_browser

    echo ""
    echo "==================================================="
    echo "  VulnSuite is running in Docker mode!"
    echo "  URL: $URL"
    echo "  View live logs: $COMPOSE_CMD logs -f"
    echo "  Stop lab:       $COMPOSE_CMD down"
    echo "==================================================="
    exit 0
fi

# ── 2. Native Fallback (Docker not active) ───────────
echo "[!] Docker is not active. Using Native Automated Setup..."
echo ""

# Check for Python
PY_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
fi

if [ -z "$PY_CMD" ]; then
    echo "[!] Neither Docker nor Python was found on your system."
    echo "[!] Please install Docker Desktop or Python 3.11+."
    exit 1
fi

echo "[*] Python detected: $PY_CMD"

# Setup virtual environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

echo "[*] Automatically downloading and installing all Python requirements..."
pip install --quiet --upgrade pip
pip install --quiet -r backend/requirements.txt

echo "[*] Initializing database and pre-configuring seed accounts..."
DATABASE="backend/LabDatabase.db" python seed/seed.py

# Check Node.js for the internal API microservice
if command -v npm >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then
    echo "[*] Node.js detected. Automatically installing internal-api requirements..."
    npm install --prefix internal-api --silent
    echo "[*] Starting internal API service in background..."
    node internal-api/server.js >/dev/null 2>&1 &
fi

# Start Flask backend on port 9999
echo "[*] Starting VulnSuite portal on $URL..."
PORT=9999 DATABASE="backend/LabDatabase.db" python backend/app.py &
BACKEND_PID=$!

sleep 3
open_browser

echo ""
echo "==================================================="
echo "  VulnSuite is running in Native Python mode!"
echo "  URL: $URL"
echo "  Press Ctrl+C to stop the server."
echo "==================================================="

# Wait on backend process
wait $BACKEND_PID
