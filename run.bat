@echo off
setlocal

:: Change to the script's directory
cd /d "%~dp0"

echo ==========================================
echo  Soccer Prediction App Launcher
echo ==========================================

echo Current directory: %cd%

echo .

:: Step 1: Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Step 2: Install dependencies (after venv activation)
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

:: Verify installation
echo.
if errorlevel 1 (
    echo ERROR: pip install failed!
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!

:: Step 3: Launch the app
echo.
echo launching soccer prediction app...
echo.
streamlit run app.py

:: Keep terminal open after app closes
pause