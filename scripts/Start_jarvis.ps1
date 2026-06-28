# ==============================
# JARVIS BOOT SYSTEM
# ==============================

$logFile = "$PSScriptRoot\jarvis_boot.log"

# ---- LOG SETUP ----
if (!(Test-Path $PSScriptRoot)) {
    New-Item -ItemType Directory -Path $PSScriptRoot | Out-Null
}

function Log($msg, $color = "White") {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line -ForegroundColor $color
    Add-Content -Path $logFile -Value $line
}

Log "=== JARVIS STARTUP INITIATED ==="

function Test-OllamaAPI {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

Clear-Host

Write-Host "==============================" -ForegroundColor Cyan
Write-Host "     JARVIS BOOT SYSTEM" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

Log "Boot sequence started" "Cyan"

# ==============================
# MODEL SELECTION
# ==============================

Write-Host ""
Write-Host "1 - glm-4.7-flash (General)"
Write-Host "2 - qwen2.5-coder (Coding)"
Write-Host "3 - deepseek-coder (Reasoning)"
Write-Host ""

$modelChoice = Read-Host "Select model (1-3)"

if ($modelChoice -eq "2") {
    $model = "qwen2.5-coder:latest"
}
elseif ($modelChoice -eq "3") {
    $model = "deepseek-coder:latest"
}
else {
    $model = "glm-4.7-flash:latest"
}

Log "Model selected: $model" "Green"

# ==============================
# STEP 1 - OLLAMA PROCESS
# ==============================

Log "STEP 1: Checking Ollama process..."

$proc = Get-Process ollama -ErrorAction SilentlyContinue

if ($proc -eq $null) {
    Log "Ollama not running. Starting..." "Yellow"
    Start-Process "ollama" -ArgumentList "serve"
    Start-Sleep -Seconds 4
}
else {
    Log "Ollama running (PID $($proc.Id))" "Green"
}

# ==============================
# STEP 2 - PORT CHECK
# ==============================

Log "STEP 2: Waiting for port 11434..."

$portReady = $false
$i = 0

while ($i -lt 15) {

    if (Test-Port 11434) {
        Log "Port 11434 is open OK" "Green"
        $portReady = $true
        break
    }

    Log "Waiting for port... ($i/15)" "Yellow"
    Start-Sleep -Seconds 2
    $i++
}

if ($portReady -eq $false) {
    Log "Port failed. Restarting Ollama..." "Red"

    Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Start-Process "ollama" -ArgumentList "serve"
    Start-Sleep -Seconds 5
}

# ==============================
# STEP 3 - API CHECK
# ==============================

Log "STEP 3: Checking API..."

$apiReady = $false
$i = 0

while ($i -lt 20) {

    if (Test-OllamaAPI) {
        Log "API responding OK" "Green"
        $apiReady = $true
        break
    }

    Log "API not ready... ($i/20)" "Yellow"
    Start-Sleep -Seconds 2
    $i++
}

if ($apiReady -eq $false) {
    Log "FATAL: API not responding" "Red"
    exit 1
}

# ==============================
# STEP 4 - MODEL WARMUP
# ==============================

Log "STEP 4: Warming up model..."

$body = @{
    model  = $model
    prompt = "Respond with OK only"
    stream = $false
} | ConvertTo-Json -Depth 3

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30 | Out-Null
    Log "Model warmup successful OK" "Green"
}
catch {
    Log "Model warmup failed" "Red"
    exit 1
}

Log "JARVIS READY SYSTEM ONLINE" "Green"

# ---- FINAL STATUS ----
Log "Launching Jarvis chat with $model"

# ---- START CHAT ----
ollama run $model