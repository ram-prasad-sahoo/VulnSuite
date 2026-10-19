#!/usr/bin/env bash
# =========================================
#       VulnSuite Lab Startup Script
#        (Linux & macOS Quick Start)
# =========================================

set -e

# Detect operating system
OS="$(uname -s)"

echo "========================================="
echo "      VulnSuite Lab Startup Script       "
echo "========================================="
echo ""

# 1. Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Docker is not installed."
    echo "[!] Please install Docker / Docker Desktop before running this lab."
    exit 1
fi

# 2. Check if Docker daemon is running
echo "[*] Checking if Docker daemon is running..."
if ! docker info >/dev/null 2>&1; then
    echo "[!] Docker daemon is not running."
    echo "[!] Please start Docker Desktop or the docker service (e.g. 'sudo systemctl start docker')."
    echo "[*] Waiting for Docker to start..."
    while ! docker info >/dev/null 2>&1; do
        sleep 3
        echo "    ...still waiting for Docker..."
    done
fi

echo "[*] Docker is running!"

# 3. Determine compose command ('docker compose' vs 'docker-compose')
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo "[!] Neither 'docker compose' nor 'docker-compose' was found."
    exit 1
fi

# 4. Build and start containers in the background
echo "[*] Launching containers via '$COMPOSE_CMD'..."
$COMPOSE_CMD up --build -d

echo "[*] Waiting 6 seconds for the web server and database to spin up..."
sleep 6

# 5. Open browser automatically
URL="http://localhost:9999"
echo "[*] Opening the lab in your default web browser ($URL)..."
if [ "$OS" = "Darwin" ]; then
    open "$URL" >/dev/null 2>&1 || true
elif [ "$OS" = "Linux" ]; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
    elif command -v sensible-browser >/dev/null 2>&1; then
        sensible-browser "$URL" >/dev/null 2>&1 || true
    fi
fi

echo ""
echo "========================================="
echo "  Lab is ready at: $URL"
echo "  To view live logs:  $COMPOSE_CMD logs -f"
echo "  To stop the lab:    $COMPOSE_CMD down"
echo "========================================="
