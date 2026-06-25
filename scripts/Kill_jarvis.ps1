Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "Jarvis stopped."