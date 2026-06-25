```powershell
# ============================================================
# JARVIS CONTROL CENTER
# Version 2.0 - With Multi-Level Logging
# ============================================================

$ModelPath = "F:\media\Models\ollama-models"
$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$JarvisPath = "C:\App\Ai"
$PythonExe = "python"
$LogDir = "C:\App\Ai\logs"
$VoiceLogFile = "$LogDir\voice_assistant.log"

# Logging levels: QUIET, NORMAL, VERBOSE
$LogLevel = "NORMAL"

# Ensure log directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Write to file
    Add-Content -Path $VoiceLogFile -Value $logMessage
    
    # Write to console based on log level
    if ($LogLevel -eq "VERBOSE") {
        Write-Host $logMessage -ForegroundColor Gray
    }
    elseif ($LogLevel -eq "NORMAL" -and $Level -ne "DEBUG") {
        if ($Level -eq "ERROR") {
            Write-Host $logMessage -ForegroundColor Red
        }
        elseif ($Level -eq "WARN") {
            Write-Host $logMessage -ForegroundColor Yellow
        }
        else {
            Write-Host $logMessage -ForegroundColor White
        }
    }
    elseif ($LogLevel -eq "QUIET" -and $Level -eq "ERROR") {
        Write-Host $logMessage -ForegroundColor Red
    }
}

function Set-LogLevel {
    param(
        [string]$Level
    )
    $script:LogLevel = $Level
    Log "Log level set to: $Level" "INFO"
}

function Show-LogFile {
    Clear-Host
    Write-Host ""
    Write-Host "=== VOICE ASSISTANT LOG ===" -ForegroundColor Cyan
    Write-Host "Log file: $VoiceLogFile" -ForegroundColor Gray
    Write-Host ""
    
    if (Test-Path $VoiceLogFile) {
        Get-Content $VoiceLogFile -Tail 100
    }
    else {
        Write-Host "No logs available yet." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Pause-Jarvis
}

function Clear-LogFile {
    if (Test-Path $VoiceLogFile) {
        Clear-Content $VoiceLogFile
        Write-Host "Log file cleared." -ForegroundColor Green
    }
    Pause-Jarvis
}

function Pause-Jarvis {
    Write-Host ""
    Read-Host "Press ENTER to continue"
}

function Get-VoiceAssistantStatus {
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

    if ($proc) {
        return "RUNNING (PID $($proc.Id))"
    }

    return "STOPPED"
}

function Wait-OllamaReady {
    Write-Host "Waiting for Ollama to be ready..." -ForegroundColor Yellow
    
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = ollama list 2>$null
            if ($response) {
                Write-Host "Ollama is ready!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Start-Sleep 1
        }
    }
    
    Write-Host "Ollama did not respond in time." -ForegroundColor Red
    return $false
}

function Start-VoiceAssistant {
    
    Write-Host ""
    Write-Host "=== STARTING JARVIS VOICE ASSISTANT ===" -ForegroundColor Green
    Write-Host ""

    Log "Voice assistant startup initiated" "INFO"

    # Prerequisite 1: Start Ollama if not running
    if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
        Write-Host "[1/3] Starting Ollama..." -ForegroundColor Cyan
        Log "Starting Ollama server..." "DEBUG"
        Start-JarvisServer
    }
    else {
        Write-Host "[1/3] Ollama already running" -ForegroundColor Green
        Log "Ollama already running" "DEBUG"
    }

    # Prerequisite 2: Wait for Ollama to be ready
    Write-Host "[2/3] Checking Ollama readiness..." -ForegroundColor Cyan
    Log "Checking Ollama readiness..." "DEBUG"
    if (-not (Wait-OllamaReady)) {
        Write-Host "Failed to start Ollama. Aborting." -ForegroundColor Red
        Log "Ollama failed to respond. Startup aborted." "ERROR"
        Pause-Jarvis
        return
    }

    # Prerequisite 3: Check if voice assistant already running
    if (Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }) {
        Write-Host "Voice assistant already running!" -ForegroundColor Yellow
        Log "Voice assistant already running" "WARN"
        Pause-Jarvis
        return
    }

    # Start the voice assistant
    Write-Host "[3/3] Starting voice assistant..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Launching Jarvis voice listening mode..." -ForegroundColor Green
    Write-Host ""
    
    Log "Launching Python main.py..." "DEBUG"

    Set-Location $JarvisPath

    try {
        # Capture output to log file
        $process = Start-Process `
            -FilePath $PythonExe `
            -ArgumentList "main.py" `
            -WindowStyle Normal `
            -RedirectStandardOutput "$LogDir\voice_stdout.tmp" `
            -RedirectStandardError "$LogDir\voice_stderr.tmp" `
            -PassThru

        Log "Voice assistant started with PID $($process.Id)" "INFO"
        
        Write-Host "Voice assistant launched!" -ForegroundColor Green
        Write-Host "Process ID: $($process.Id)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Logs are being saved to: $VoiceLogFile" -ForegroundColor Gray
        Write-Host ""
        
        # Monitor for crashes
        Start-Sleep 2
        
        if ($process.HasExited) {
            Write-Host ""
            Write-Host "ERROR: Voice assistant exited immediately!" -ForegroundColor Red
            Write-Host ""
            
            $stderr = Get-Content "$LogDir\voice_stderr.tmp" -ErrorAction SilentlyContinue
            if ($stderr) {
                Write-Host "STDERR:" -ForegroundColor Red
                Write-Host $stderr
                Log "Python stderr: $stderr" "ERROR"
            }
            
            $stdout = Get-Content "$LogDir\voice_stdout.tmp" -ErrorAction SilentlyContinue
            if ($stdout) {
                Write-Host ""
                Write-Host "STDOUT:" -ForegroundColor Yellow
                Write-Host $stdout
                Log "Python stdout: $stdout" "ERROR"
            }
        }
        else {
            Write-Host "Voice assistant is running. Check logs for activity." -ForegroundColor Green
        }
        
    }
    catch {
        Write-Host "Error launching voice assistant: $_" -ForegroundColor Red
        Log "Launch error: $_" "ERROR"
    }
    
    Pause-Jarvis
}

function Stop-VoiceAssistant {
    
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }

    if ($proc) {
        Stop-Process -InputObject $proc -Force -ErrorAction SilentlyContinue
        Write-Host "Voice assistant stopped." -ForegroundColor Yellow
    }
    else {
        Write-Host "Voice assistant is not running." -ForegroundColor Yellow
    }
    
    Pause-Jarvis
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

    Write-Host "Ollama Status    : $(Get-OllamaStatus)" -ForegroundColor Yellow
    Write-Host "Voice Assistant  : $(Get-VoiceAssistantStatus)" -ForegroundColor Yellow
    Write-Host "Log Level        : $LogLevel" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "QUICK START" -ForegroundColor Green
    Write-Host "9 - START VOICE ASSISTANT (All Prerequisites)" -ForegroundColor Green
    Write-Host ""
    Write-Host "LOGGING" -ForegroundColor Cyan
    Write-Host "11 - View Voice Assistant Logs"
    Write-Host "12 - Clear Voice Assistant Logs"
    Write-Host "13 - Set Log Level (Verbose/Normal/Quiet)"
    Write-Host ""
    Write-Host "OLLAMA CONTROLS"
    Write-Host "1 - Start Ollama"
    Write-Host "2 - Stop Ollama"
    Write-Host "3 - Status"
    Write-Host ""
    Write-Host "VOICE ASSISTANT"
    Write-Host "10 - Stop Voice Assistant"
    Write-Host ""
    Write-Host "MODELS"
    Write-Host "4 - GLM 4.7 Flash"
    Write-Host "5 - Qwen 2.5 Coder"
    Write-Host "6 - Qwen 3"
    Write-Host ""
    Write-Host "SYSTEM"
    Write-Host "7 - List Installed Models"
    Write-Host "8 - GPU Status"
    Write-Host ""
    Write-Host "0 - Exit"
    Write-Host ""

    $choice = Read-Host "Select option"

    switch ($choice) {

        "9" {
            Start-VoiceAssistant
        }

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

        "10" {
            Stop-VoiceAssistant
        }

        "11" {
            Show-LogFile
        }

        "12" {
            Clear-LogFile
        }

        "13" {
            Clear-Host
            Write-Host "Current Log Level: $LogLevel" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "1 - VERBOSE (Show all messages including DEBUG)"
            Write-Host "2 - NORMAL (Show INFO, WARN, ERROR)"
            Write-Host "3 - QUIET (Show only ERROR)"
            Write-Host ""
            $logChoice = Read-Host "Select log level"
            
            switch ($logChoice) {
                "1" { Set-LogLevel "VERBOSE" }
                "2" { Set-LogLevel "NORMAL" }
                "3" { Set-LogLevel "QUIET" }
                default { Write-Host "Invalid selection." -ForegroundColor Red }
            }
            
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
