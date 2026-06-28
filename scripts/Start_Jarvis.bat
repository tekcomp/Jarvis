@echo off
setlocal enabledelayedexpansion

echo ========================================
echo JARVIS START BATCH SCRIPT
echo ========================================
echo [%date% %time%] Starting JARVIS...
echo Current directory: %cd%
echo PowerShell script: %~dp0Start_jarvis.ps1
echo.

pushd "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start_jarvis.ps1"
set PS_EXIT_CODE=%ERRORLEVEL%
popd

echo.
echo ========================================
echo [%date% %time%] Batch script complete
echo PowerShell exit code: %PS_EXIT_CODE%
echo ========================================
echo.

if %PS_EXIT_CODE% NEQ 0 (
    echo ERROR: PowerShell script failed with exit code %PS_EXIT_CODE%
)

pause
endlocal