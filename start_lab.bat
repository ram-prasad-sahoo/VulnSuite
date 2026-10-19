@echo off
setlocal

echo =========================================
echo       VulnSuite Lab Startup Script
echo =========================================
echo.

echo [*] Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% equ 0 goto docker_running

echo [!] Docker is not running.
echo [!] Please launch "Docker Desktop" from your Windows Start menu now.
echo [*] The script will wait automatically until it detects Docker is running...
:wait_docker
timeout /t 5 /nobreak >nul
docker info >nul 2>&1
if errorlevel 1 (
    echo ...still waiting...
    goto wait_docker
)

:docker_running
echo [*] Docker is running!

echo [*] Starting docker-compose in a new window...
:: Launch docker-compose in a new command prompt window so this script can continue
start "VulnSuite Lab Server" cmd /c "docker-compose up --build"

echo [*] Waiting 10 seconds for the Flask server and database to spin up...
timeout /t 10 /nobreak >nul

echo [*] Opening the lab in your default web browser...
start http://localhost:9999

echo.
echo =========================================
echo   Lab is ready! 
echo   (To stop the lab later, close the server window and run 'docker-compose down')
echo =========================================
pause
