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

# ── 1. Clean up any existing zombie processes on ports 9999 and 3000 ─
if command -v lsof >/dev/null 2>&1; then
    PID_9999=$(lsof -ti:9999 2>/dev/null || true)
    if [ -n "$PID_9999" ]; then
        echo "[*] Port 9999 is currently busy. Releasing port (PID: $PID_9999)..."
        kill -9 $PID_9999 2>/dev/null || true
    fi
    PID_3000=$(lsof -ti:3000 2>/dev/null || true)
    if [ -n "$PID_3000" ]; then
        kill -9 $PID_3000 2>/dev/null || true
    fi
fi

# ── 2. Check if Docker is available and running ──────
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

    echo "[*] Launching containers and streaming live server logs..."
    (sleep 6 && open_browser) &

    echo ""
    echo "==================================================="
    echo "  VulnSuite Server Running (Docker Mode)"
    echo "  URL: $URL"
    echo "  Streaming live HTTP requests and responses below..."
    echo "  Press Ctrl+C to stop the server."
    echo "==================================================="
    echo ""

    $COMPOSE_CMD up --build
    exit 0
fi

# ── 3. Native Fallback (Docker not active) ───────────
echo "[!] Docker is not active. Using Native Automated Setup..."
echo ""

# Detect Python 3 reliably
PY_CMD=""
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
        PY_CMD="python3"
    fi
fi

if [ -z "$PY_CMD" ] && command -v python >/dev/null 2>&1; then
    if python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
        PY_CMD="python"
    fi
fi

if [ -z "$PY_CMD" ]; then
    echo "==================================================="
    echo "[!] ERROR: Python 3 was not found on your system!"
    echo "[!] VulnSuite requires Python 3.10, 3.11, or 3.12."
    echo "[!] Please install Python 3 or Docker Desktop."
    echo "==================================================="
    exit 1
fi

echo "[*] Python 3 detected: $PY_CMD"

# Verify or create virtual environment
REBUILD_VENV=false
if [ ! -f ".venv/bin/python" ]; then
    REBUILD_VENV=true
else
    if ! .venv/bin/python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
        echo "[*] Existing virtual environment is incompatible. Rebuilding..."
        rm -rf .venv
        REBUILD_VENV=true
    fi
fi

if [ "$REBUILD_VENV" = true ]; then
    echo "[*] Creating virtual environment (.venv)..."
    if ! $PY_CMD -m venv .venv 2>/dev/null; then
        echo "[!] Failed to create .venv. Falling back to system python."
        RUN_PY="$PY_CMD"
    else
        RUN_PY=".venv/bin/python"
    fi
else
    RUN_PY=".venv/bin/python"
fi

# Install Python requirements
echo "[*] Checking and installing Python dependencies..."
"$RUN_PY" -m pip install --quiet --upgrade pip 2>/dev/null || true
"$RUN_PY" -m pip install --quiet -r backend/requirements.txt || {
    echo "[!] Warning: Some dependencies could not be downloaded."
    echo "[*] Attempting to continue with installed packages..."
}

echo "[*] Initializing database and pre-configuring seed accounts..."
DATABASE="backend/LabDatabase.db" "$RUN_PY" seed/seed.py >/dev/null 2>&1

# Check Node.js for the internal API microservice
if command -v npm >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then
    if [ ! -d "internal-api/node_modules" ]; then
        echo "[*] Installing internal-api microservice dependencies..."
        npm install --prefix internal-api --silent >/dev/null 2>&1 || true
    fi
    echo "[*] Starting internal API service in background..."
    node internal-api/server.js >/dev/null 2>&1 &
else
    echo "[*] Node.js not detected. Skipping internal microservice (Core Web Portal is fully operational)."
fi

echo ""
echo "==================================================="
echo "  VulnSuite Backend Server Ready!"
echo "  Web Portal URL: $URL"
echo "  All incoming HTTP requests and responses stream below:"
echo "  Do NOT close this terminal. Press Ctrl+C to stop."
echo "==================================================="
echo ""

(sleep 3 && open_browser) &

# Run Flask backend in foreground so terminal stays active and shows all requests/responses
PORT=9999 DATABASE="backend/LabDatabase.db" "$RUN_PY" backend/app.py


