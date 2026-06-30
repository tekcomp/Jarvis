$pidFile = "C:\App\AI\state\kernel.pid"

# Stop audio kernel (PID marker)
if (Test-Path $pidFile) {
    try {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Stopping Jarvis audio kernel (PID $pid) - announcing shutdown..."
                # Graceful: send SIGTERM-equivalent via CloseMainWindow; fall back to -Force after grace.
                $proc.CloseMainWindow() | Out-Null
                if (-not $proc.WaitForExit(5000)) {
                    Write-Host "Graceful shutdown timed out, forcing..."
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
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