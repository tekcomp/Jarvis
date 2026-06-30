$pidFile = "C:\App\AI\state\kernel.pid"
$kernelModule = "core.alive_kernel"

# ---- Helper: stop a PID with grace, then force ----
function Stop-KernelProcess {
    param([int]$targetPid)
    $p = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if (-not $p) { return }
    Write-Host "Stopping audio kernel (PID $targetPid) - announcing shutdown..."
    $p.CloseMainWindow() | Out-Null
    if (-not $p.WaitForExit(5000)) {
        Write-Host "Graceful shutdown timed out, forcing..."
        Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue
    }
}

# ---- 1. Stop the marked kernel (graceful) ----
$markerStopped = $false
if (Test-Path $pidFile) {
    try {
        $kernelPid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($kernelPid) {
            Stop-KernelProcess -targetPid ([int]$kernelPid)
            $markerStopped = $true
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
    catch {
        Write-Host "Kernel kill error: $_"
    }
}
else {
    Write-Host "No kernel.pid marker found - sweeping for Jarvis kernel processes..."
}

# ---- 2. Sweep: force-stop any python.exe started inside C:\App\AI ----
try {
    $candidates = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'"
    $orphans = @()
    foreach ($proc in $candidates) {
        $cmd = $proc.CommandLine
        if ($cmd -and ($cmd -like "*C:\App\AI*" -or $cmd -like "*\\App\\AI\\*")) {
            # exclude obvious non-app python (jupyter, ipython REPL tag etc.)
            if ($cmd -notmatch "jupyter|ipython|code --ms-enable-electron|pycharm") {
                $orphans += $proc.ProcessId
            }
        }
    }
    if ($orphans.Count -gt 0) {
        Write-Host "Found $($orphans.Count) orphan Jarvis-kernel process(es); force-stopping."
        foreach ($orphan in $orphans) {
            Stop-Process -Id $orphan -Force -ErrorAction SilentlyContinue
            Write-Host "  -> killed PID $orphan"
        }
    }
    else {
        Write-Host "No orphan Jarvis-kernel python processes found."
    }
}
catch {
    Write-Host "Sweep error (non-fatal): $_"
}

# ---- 3. Stop Ollama ----
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "Jarvis stopped."