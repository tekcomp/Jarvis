$pidFile = "C:\App\AI\state\kernel.pid"

# Stop audio kernel (PID marker).
# NOTE: $PID is a reserved PowerShell automatic variable; use $kernelPid to avoid collisions.
if (Test-Path $pidFile) {
    try {
        $kernelPid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($kernelPid) {
            $proc = Get-Process -Id $kernelPid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Stopping Jarvis audio kernel (PID $kernelPid) - announcing shutdown..."
                # Graceful: send SIGTERM-equivalent via CloseMainWindow; fall back to -Force after grace.
                $proc.CloseMainWindow() | Out-Null
                if (-not $proc.WaitForExit(5000)) {
                    Write-Host "Graceful shutdown timed out, forcing..."
                    Stop-Process -Id $kernelPid -Force -ErrorAction SilentlyContinue
                }
            }
            Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Host "Kernel kill error: $_"
    }
}
else {
    Write-Host "No kernel.pid marker found - audio kernel may not be running."
}

Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "Jarvis stopped."