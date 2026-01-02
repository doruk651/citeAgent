@echo off
REM Script to start Chrome in debug mode for CiteAgent (Windows)

SET DEBUG_PORT=9222
SET USER_DATA_DIR=C:\ChromeProfile
SET CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe

echo Starting Chrome in debug mode...
echo Debug port: %DEBUG_PORT%
echo User data directory: %USER_DATA_DIR%
echo.
echo After Chrome opens:
echo 1. Navigate to https://www.overleaf.com
echo 2. Log in and open your project
echo 3. Run: python main.py --interactive
echo.

start "" "%CHROME_PATH%" --remote-debugging-port=%DEBUG_PORT% --user-data-dir="%USER_DATA_DIR%"

echo Chrome started!
pause
