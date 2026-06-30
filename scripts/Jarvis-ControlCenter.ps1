# ============================================================
# JARVIS CONTROL CENTER
# Version 2.1 - With Multi-Level Logging + Graceful Kill
# ============================================================

# ============================================================
# CONFIGURATION
# ============================================================
$JarvisPath = "$env:USERPROFILE\Jarvis"
$LogPath = "C:\App\Ai\logs\logs.txt"
$LogLevel = "NORMAL" # Options: VERBOSE, NORMAL, QUIET
$OllamaExe = "ollama.exe" # Ensure 'ollama' is in your PATH or provide full path

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Log {
    param([string]$message, [string]$level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$level] $message"
    
    # Write to console based on level
    switch ($level) {
        "DEBUG" { if ($LogLevel -eq "VERBOSE") { Write-Host $logEntry -ForegroundColor DarkGray } }
        "INFO" { if ($LogLevel -ne "QUIET") { Write-Host $logEntry -ForegroundColor Cyan } }
        "WARN" { if ($LogLevel -ne "QUIET") { Write-Host $logEntry -ForegroundColor Yellow } }
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
    }

    # Write to file
    Add-Content -Path $LogPath -Value $logEntry
}

function Get-VoiceAssistantStatus {
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($proc) { return "Running" }
    return "Stopped"
}

function Wait-Jarvis {
    param([int]$seconds = 2)
    Start-Sleep -Seconds $seconds
}

function Show-LogFile {
    if (Test-Path $LogPath) {
        Get-Content $LogPath | Select-Object -Last 50
    }
    else {
        Write-Host "Log file not found." -ForegroundColor Yellow
    }
}

function Clear-LogFile {
    if (Test-Path $LogPath) {
        Remove-Item $LogPath
        Write-Host "Log cleared." -ForegroundColor Green
    }
}

function Set-LogLevel {
    param([string]$level)
    $validLevels = @("VERBOSE", "NORMAL", "QUIET")
    if ($level -in $validLevels) {
        $global:LogLevel = $level
        Write-Host "Log level set to: $level" -ForegroundColor Green
    }
    else {
        Write-Host "Invalid level. Use VERBOSE, NORMAL, or QUIET." -ForegroundColor Red
    }
}

function Launch-Model {
    param([string]$model)
    Write-Host "Launching model: $model" -ForegroundColor Cyan
    Start-Process -FilePath "ollama" -ArgumentList "run $model"
}

# ============================================================
# MAIN FUNCTIONS
# ============================================================

function Start-VoiceAssistant {
    Write-Host "Starting JARVIS..." -ForegroundColor Green
    Log "Starting JARVIS..."
    
    # Check if python is installed
    $pythonCheck = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCheck) {
        Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
        Log "Error: Python not found."
        return
    }

    # Start the main script
    Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Normal
}

function Stop-VoiceAssistant {
    Write-Host "Stopping JARVIS..." -ForegroundColor Yellow
    Log "Stopping JARVIS..."
    
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    
    if ($proc) {
        # Try graceful shutdown first (writing to file)
        $stopFile = "$JarvisPath\stop_signal.txt"
        Set-Content -Path $stopFile -Value "shutdown"
        
        # Wait a moment for graceful exit
        Start-Sleep -Seconds 2
        
        # Force kill if still running
        if ($proc) {
            Write-Host "Force killing Python process..." -ForegroundColor Red
            $proc | Stop-Process -Force
        }
        Write-Host "JARVIS stopped." -ForegroundColor Green
    }
    else {
        Write-Host "JARVIS is not running." -ForegroundColor Yellow
    }
}

function Stop-VoiceAssistantGracefully {
    Write-Host "Sending graceful shutdown signal..." -ForegroundColor Yellow
    Log "Sending graceful shutdown signal..."
    
    $stopFile = "$JarvisPath\stop_signal.txt"
    Set-Content -Path $stopFile -Value "shutdown"
    
    # Wait for the process to read the file and exit
    Start-Sleep -Seconds 3
    Write-Host "Signal sent." -ForegroundColor Green
}

# ============================================================
# MENU LOOP
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   JARVIS CONTROL CENTER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

while ($true) {
    Write-Host "`n[1] Start JARVIS" -ForegroundColor White
    Write-Host "[2] Stop JARVIS (Force)" -ForegroundColor White
    Write-Host "[3] Stop JARVIS (Graceful)" -ForegroundColor White
    Write-Host "[4] Launch Ollama Model" -ForegroundColor White
    Write-Host "[5] View Logs" -ForegroundColor White
    Write-Host "[6] Clear Logs" -ForegroundColor White
    Write-Host "[7] Set Log Level (VERBOSE/NORMAL/QUIET)" -ForegroundColor White
    Write-Host "[0] Exit" -ForegroundColor White
    
    $choice = Read-Host "Please select an option"

    switch ($choice) {
        "1" { Start-VoiceAssistant }
        "2" { Stop-VoiceAssistant }
        "3" { Stop-VoiceAssistantGracefully }
        "4" { 
            $model = Read-Host "Enter model name (e.g., llama2)"
            Launch-Model -model $model
        }
        "5" { Show-LogFile }
        "6" { Clear-LogFile }
        "7" { 
            $level = Read-Host "Enter level (VERBOSE/NORMAL/QUIET)"
            Set-LogLevel -level $level
        }
        "0" { 
            Write-Host "Exiting..." -ForegroundColor Yellow
            exit 
        }
        default { Write-Host "Invalid option." -ForegroundColor Red }
    }
    
    Wait-Jarvis
}