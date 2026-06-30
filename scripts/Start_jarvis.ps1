# ===============================
# JARVIS ZERO-FRICTION LAUNCHER
# ===============================

$ErrorActionPreference = "SilentlyContinue"

# ---- CONFIG ----
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$modelDrive = "F:\media\Models\ollama-models"
$defaultModel = "llama3"
$logDir = "C:\App\Ai\Logs"
$logFile = "$logDir\jarvis.log"

# ---- LOG SETUP ----
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

function Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Log "=== JARVIS STARTUP INITIATED ==="

# ---- CHECK MODEL DRIVE ----
if (!(Test-Path $modelDrive)) {
    Log "ERROR: Model drive not found: $modelDrive"
    exit 1
}

# ---- ENSURE OLLAMA MODELS PATH ----
$env:OLLAMA_MODELS = $modelDrive
Log "Model path set to $modelDrive"

# ---- CHECK IF OLLAMA IS RUNNING ----
$ollamaProc = Get-Process ollama -ErrorAction SilentlyContinue

if ($ollamaProc) {
    Log "Ollama already running (PID: $($ollamaProc.Id))"
}
else {
    Log "Starting Ollama server..."
    Start-Process -FilePath $ollamaPath -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# ---- VERIFY MODEL EXISTS ----
$models = ollama list

if (-not ($models -match $defaultModel)) {
    Log "Default model missing. Pulling $defaultModel..."
    ollama pull $defaultModel
}

# ---- FINAL STATUS ----
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) {
    Log "ERROR: 'python' not found on PATH"
    exit 1
}
Log "Python: $py"

# ---- START AUDIO KERNEL ----
Log "Launching Jarvis AUDIO agent (alive_kernel)"
Set-Location "C:\App\AI"
& python -c "from core.alive_kernel import start_kernel; start_kernel()"
exit $LASTEXITCODE