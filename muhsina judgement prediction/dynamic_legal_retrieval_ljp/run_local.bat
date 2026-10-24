@echo off
title DLKR-LJP Local Launcher
echo =====================================================================
echo  Starting DLKR-LJP (Legal Judgment Prediction Engine) Locally
echo =====================================================================
echo.
cd /d "%~dp0"

echo [1/2] Checking Gradio dependency...
python -c "import gradio" 2>nul
if %errorlevel% neq 0 (
    echo Gradio not found. Installing gradio for local web UI...
    pip install gradio
)

echo.
echo [2/2] Launching DLKR-LJP Dashboard at http://localhost:7860 ...
python standalone_dlkr_ljp.py
pause
