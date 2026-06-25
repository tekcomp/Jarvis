```powershell
# ============================================================
# JARVIS CONTROL CENTER
# Version 1.0
# ============================================================

$ModelPath = "F:\media\Models\ollama-models"
$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

function Pause-Jarvis {
    Write-Host ""
    Read-Host "Press ENTER to continue"
}

function Show-Header {
    Clear-Host
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "        JARVIS CONTROL CENTER         " -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
}

function Get-OllamaStatus {
    $proc = Get-Process ollama -ErrorAction SilentlyContinue

    if ($proc) {
        return "RUNNING (PID $($proc.Id))"
    }

    return "STOPPED"
}

function Start-JarvisServer {

    if (Get-Process ollama -ErrorAction SilentlyContinue) {
        Write-Host "Ollama already running." -ForegroundColor Yellow
        return
    }

    $env:OLLAMA_MODELS = $ModelPath

    Start-Process `
        -FilePath $OllamaExe `
        -ArgumentList "serve" `
        -WindowStyle Hidden

    Start-Sleep 5

    Write-Host "Ollama started." -ForegroundColor Green
}

function Stop-JarvisServer {

    Get-Process ollama -ErrorAction SilentlyContinue |
    Stop-Process -Force

    Write-Host "Ollama stopped." -ForegroundColor Yellow
}

function Show-SystemStatus {

    Clear-Host

    Write-Host "JARVIS STATUS" -ForegroundColor Cyan
    Write-Host "--------------------------------------"

    Write-Host ""
    Write-Host "Model Path:"
    Write-Host "  $ModelPath"

    Write-Host ""
    Write-Host "Path Exists:"
    Write-Host "  $(Test-Path $ModelPath)"

    Write-Host ""
    Write-Host "Ollama:"
    Write-Host "  $(Get-OllamaStatus)"

    Write-Host ""
    Write-Host "Installed Models:"
    ollama list

    Write-Host ""
    Pause-Jarvis
}

function Launch-Model {

    param(
        [string]$Model
    )

    if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
        Start-JarvisServer
    }

    Clear-Host

    Write-Host ""
    Write-Host "Launching $Model..." -ForegroundColor Green
    Write-Host ""

    ollama run $Model
}

while ($true) {

    Show-Header

    Write-Host "Ollama Status : $(Get-OllamaStatus)"
    Write-Host ""
    Write-Host "1 - Start Ollama"
    Write-Host "2 - Stop Ollama"
    Write-Host "3 - Status"
    Write-Host ""
    Write-Host "MODELS"
    Write-Host "4 - GLM 4.7 Flash"
    Write-Host "5 - Qwen 2.5 Coder"
    Write-Host "6 - Qwen 3"
    Write-Host ""
    Write-Host "7 - List Installed Models"
    Write-Host "8 - GPU Status"
    Write-Host ""
    Write-Host "0 - Exit"
    Write-Host ""

    $choice = Read-Host "Select option"

    switch ($choice) {

        "1" {
            Start-JarvisServer
            Pause-Jarvis
        }

        "2" {
            Stop-JarvisServer
            Pause-Jarvis
        }

        "3" {
            Show-SystemStatus
        }

        "4" {
            Launch-Model "glm-4.7-flash"
        }

        "5" {
            Launch-Model "qwen2.5-coder:14b"
        }

        "6" {
            Launch-Model "qwen3:14b"
        }

        "7" {
            Clear-Host
            ollama list
            Pause-Jarvis
        }

        "8" {
            Clear-Host
            nvidia-smi
            Pause-Jarvis
        }

        "0" {
            break
        }

        default {
            Write-Host "Invalid selection." -ForegroundColor Red
            Start-Sleep 1
        }
    }
}
```
