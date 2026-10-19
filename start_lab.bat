@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo             VulnSuite Lab Startup
echo ===================================================
echo.

:: 1. Check if Docker is available and running
where docker >nul 2>&1
if %errorlevel% neq 0 goto fallback_native

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker is installed but daemon is not running.
    echo [*] Attempting Docker wait (4 seconds)...
    timeout /t 4 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 goto fallback_native
)

:docker_mode
echo [*] Docker is running!
echo [*] Automatically building environment and installing all dependencies...
start "VulnSuite Server (Docker)" cmd /c "docker-compose up --build"
echo [*] Waiting for web application to initialize...
timeout /t 8 /nobreak >nul
start http://localhost:9999
goto finish

:fallback_native
echo.
echo ===================================================
echo [*] Docker is not active. Using Native Python Mode.
echo ===================================================
echo.

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Neither Docker nor Python was found on your system!
        echo [!] Please install either Docker Desktop OR Python 3.11+.
        echo.
        pause
        exit /b 1
    )
    set PY_CMD=py
) else (
    set PY_CMD=python
)

echo [*] Python detected (%PY_CMD%).
if not exist ".venv" (
    echo [*] Creating virtual environment in .venv...
    %PY_CMD% -m venv .venv
)

call .venv\Scripts\activate.bat

echo [*] Automatically downloading and installing all Python requirements...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r backend\requirements.txt

echo [*] Initializing database and pre-configuring seed accounts...
set DATABASE=backend\LabDatabase.db
python seed\seed.py

:: Check Node.js for the internal API microservice
where npm >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Node.js detected. Automatically installing internal-api requirements...
    cmd /c "npm install --prefix internal-api --silent"
    echo [*] Starting internal API service in background...
    start /b node internal-api\server.js >nul 2>&1
)

:: Start Backend on port 9999
echo [*] Starting VulnSuite portal on http://localhost:9999...
start "VulnSuite Portal (Native)" cmd /c "call .venv\Scripts\activate.bat && set PORT=9999 && set DATABASE=backend\LabDatabase.db && python backend\app.py"

timeout /t 4 /nobreak >nul
start http://localhost:9999

:finish
echo.
echo ===================================================
echo   VulnSuite is launched!
echo   Portal URL: http://localhost:9999
echo ===================================================
echo.
pause
