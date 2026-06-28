@echo off
REM ==========================================
REM JARVIS AI SETUP SCRIPT - WINDOWS
REM One-time environment configuration
REM ==========================================

setlocal EnableDelayedExpansion

echo ========================================
echo    JARVIS AI SETUP - WINDOWS
echo ========================================
echo.

REM Check Python version
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%
echo.

REM Check pip
echo [2/6] Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available
    exit /b 1
)
echo [OK] pip found
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Recreate? (Y/N): "
    if /i not "!RECREATE!"=="Y" (
        echo Skipping virtual environment creation
        goto :skip_venv
    ) else (
        rmdir /s /q venv
    )
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

:skip_venv

REM Activate virtual environment
echo [4/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [5/6] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip
)
echo [OK] pip upgrade completed
echo.

REM Install dependencies
echo [6/6] Installing dependencies from requirements.txt...
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM Check for Ollama
echo ========================================
echo  MODEL SETUP
echo ========================================
echo.
echo Checking for Ollama...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not running
    echo Please start Ollama from: https://ollama.com/download
    echo Then run: ollama serve
    echo.
    set /p INSTALL_MODEL="Download recommended models (gemma3, llama3.1)? (Y/N): "
    if /i "!INSTALL_MODEL!"=="Y" (
        echo.
        echo [1/2] Downloading Gemma 3...
        ollama pull gemma3
        echo [2/2] Downloading Llama 3.1...
        ollama pull llama3.1
    )
) else (
    echo [OK] Ollama is running
    echo.
    echo Available models:
    ollama list
    echo.
    set /p INSTALL_MODEL="Download additional models? (Y/N): "
    if /i "!INSTALL_MODEL!"=="Y" (
        echo.
        echo [1/2] Downloading Qwen 2.5-Coder...
        ollama pull qwen2.5-coder
        echo [2/2] Downloading DeepSeek R1...
        ollama pull deepseek-r1
    )
)
echo.

REM Create logs directory
if not exist logs mkdir logs
if not exist data mkdir data
if not exist models mkdir models
echo [OK] Directories created
echo.

REM Final message
echo ========================================
echo    SETUP COMPLETED!
echo ========================================
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run Jarvis: python main.py
echo 3. Or use: scripts\Start_jarvis_optimized.bat
echo.
echo For monitoring, run: python monitor.py
echo.
pause