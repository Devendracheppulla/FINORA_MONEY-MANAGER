@echo off

cd /d "%~dp0"

echo ==============================
echo        FINORA BACKEND
echo ==============================
echo.

echo Starting FINORA server...
echo.

uvicorn main:app --reload

pause