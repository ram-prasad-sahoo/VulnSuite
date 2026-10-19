@echo off
title VulnSuite Server Console
color 0A

echo ===================================================
echo             VulnSuite Lab Startup
echo ===================================================
echo.

:: ── 0. Automatic Update Check from GitHub ────────────
if not exist ".git" goto skip_update
where git >nul 2>&1 || goto skip_update
git remote get-url origin >nul 2>&1 || goto skip_update

echo [*] Checking for updates from GitHub...
git fetch origin --quiet 2>nul || goto skip_update

set "LOCAL_COMMIT="
set "REMOTE_COMMIT="
for /f "tokens=*" %%i in ('git rev-parse HEAD 2^>nul') do set "LOCAL_COMMIT=%%i"
for /f "tokens=*" %%i in ('git rev-parse @{u} 2^>nul') do set "REMOTE_COMMIT=%%i"

if "%REMOTE_COMMIT%"=="" goto skip_update
if "%LOCAL_COMMIT%"=="%REMOTE_COMMIT%" (
    echo [*] VulnSuite is up to date.
    goto skip_update
)

echo.
echo ===================================================
echo   A new version of VulnSuite is available!
echo ===================================================
set /p "UPDATE_CHOICE=Do you want to download and update now? (y/n): "
if /i "%UPDATE_CHOICE%"=="y" (
    echo [*] Downloading latest updates from GitHub...
    git pull --quiet
    echo [*] Updated successfully to latest version.
    echo.
)

:skip_update

:: ── 1. Clean up busy ports 9999 and 3000 ─────────────
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":9999\>.*LISTENING"') do (
    echo [*] Port 9999 is currently busy. Releasing port PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":3000\>.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: ── 2. Check if Docker is available and running ──────
set "USE_DOCKER=0"
where docker >nul 2>&1
if %errorlevel% equ 0 (
    docker info >nul 2>&1
    if %errorlevel% equ 0 set "USE_DOCKER=1"
)

if "%USE_DOCKER%"=="1" goto run_docker
goto run_native

:run_docker
echo [*] Docker is running!
echo [*] Building environment and launching VulnSuite in Docker...
echo.
echo ===================================================
echo   VulnSuite Server Running (Docker Mode)
echo   URL: http://localhost:9999
echo   All live HTTP requests and responses will show below.
echo   Press Ctrl+C to stop the server.
echo ===================================================
echo.

start /b cmd /c "ping -n 8 127.0.0.1 >nul 2>&1 && start http://localhost:9999"
docker-compose up --build

echo.
echo ===================================================
echo [!] VulnSuite Docker server stopped.
echo ===================================================
echo.
pause
exit /b 0

:run_native
echo.
echo ===================================================
echo [*] Docker is not active. Using Native Python Mode.
echo ===================================================
echo.

:: Detect Python 3 reliably
set "PY_CMD="
python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
if %errorlevel% equ 0 set "PY_CMD=python"

if "%PY_CMD%"=="" (
    py -3 -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
    if %errorlevel% equ 0 set "PY_CMD=py -3"
)

if "%PY_CMD%"=="" (
    py -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
    if %errorlevel% equ 0 set "PY_CMD=py"
)

if "%PY_CMD%"=="" (
    python3 -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
    if %errorlevel% equ 0 set "PY_CMD=python3"
)

if "%PY_CMD%"=="" (
    echo.
    echo ===================================================
    echo [!] ERROR: Python 3 was not found on your system!
    echo [!] VulnSuite requires Python 3.10, 3.11, or 3.12.
    echo [!] Download Python at: https://www.python.org/downloads/
    echo [!] (Make sure to check "Add Python to PATH" during install)
    echo ===================================================
    echo.
    pause
    exit /b 1
)

echo [*] Python 3 detected: %PY_CMD%

:: Verify or create virtual environment
set "REBUILD_VENV=0"
if not exist ".venv\Scripts\python.exe" set "REBUILD_VENV=1"

if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [*] Virtual environment is incompatible. Rebuilding...
        rmdir /s /q .venv >nul 2>&1
        set "REBUILD_VENV=1"
    )
)

if "%REBUILD_VENV%"=="1" (
    echo [*] Creating virtual environment in .venv...
    %PY_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [!] Failed to create .venv. Falling back to system python.
        set "RUN_PY=%PY_CMD%"
    ) else (
        set "RUN_PY=.venv\Scripts\python.exe"
    )
) else (
    set "RUN_PY=.venv\Scripts\python.exe"
)

:: Ensure pip and dependencies are installed
echo [*] Checking and installing Python dependencies...
"%RUN_PY%" -m pip install --quiet --upgrade pip >nul 2>&1
"%RUN_PY%" -m pip install --quiet -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [!] Warning: Some dependencies could not be downloaded.
    echo [*] Continuing with installed packages...
)

:: Initialize database
echo [*] Initializing database and pre-configuring seed accounts...
set DATABASE=backend\LabDatabase.db
"%RUN_PY%" seed\seed.py >nul 2>&1

:: Check Node.js for the internal API microservice
where npm >nul 2>&1
if %errorlevel% equ 0 (
    if not exist "internal-api\node_modules" (
        echo [*] Installing internal-api microservice dependencies...
        cmd /c "npm install --prefix internal-api --silent" >nul 2>&1
    )
    echo [*] Starting internal API service in background...
    start "VulnSuite Internal API" /b node internal-api\server.js >nul 2>&1
) else (
    echo [*] Node.js not detected. Skipping internal microservice (Core Web Portal is fully operational).
)

echo.
echo ===================================================
echo   VulnSuite Backend Server Ready!
echo   Web Portal URL: http://localhost:9999
echo   All incoming HTTP requests and responses stream below:
echo   Do NOT close this window. Press Ctrl+C to stop.
echo ===================================================
echo.

:: Automatically open browser after 3 seconds in background
start /b cmd /c "ping -n 4 127.0.0.1 >nul 2>&1 && start http://localhost:9999"

:: Run the Flask server directly in this foreground terminal window!
set PORT=9999
set DATABASE=backend\LabDatabase.db
"%RUN_PY%" backend\app.py

:: If the server ever terminates, do NOT auto-close
echo.
echo ===================================================
echo [!] VulnSuite backend server stopped.
echo ===================================================
echo.
pause
