# ==============================
#  JARVIS / OLLAMA RESET SCRIPT
#  Kill + Restart + Verify
# ==============================

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "      JARVIS RESET SCRIPT" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# 1. Kill known processes
Write-Host "`n[1/3] Stopping processes..." -ForegroundColor Yellow

$processes = @("ollama", "python", "node")

foreach ($p in $processes) {
    Get-Process -Name $p -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Also kill anything "jarvis" related if named that way
Get-Process | Where-Object { $_.ProcessName -match "jarvis" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Processes stopped." -ForegroundColor Green


# 2. Restart Ollama
Write-Host "`n[2/3] Restarting Ollama..." -ForegroundColor Yellow

Start-Sleep -Seconds 2
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 5


# 3. Verify Ollama is running
Write-Host "`n[3/3] Verifying Ollama status..." -ForegroundColor Yellow

$maxRetries = 10
$success = $false

for ($i = 1; $i -le $maxRetries; $i++) {

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 3

        if ($response) {
            Write-Host "Ollama is ONLINE ✔" -ForegroundColor Green
            $success = $true
            break
        }
    }
    catch {
        Write-Host "Attempt $i/$maxRetries - waiting..." -ForegroundColor DarkYellow
        Start-Sleep -Seconds 2
    }
}

if (-not $success) {
    Write-Host "FAILED: Ollama did not respond on port 11434" -ForegroundColor Red
    exit 1
}

Write-Host "`nJARVIS SYSTEM READY ✔" -ForegroundColor Green