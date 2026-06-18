Start-Process powershell -WindowStyle Minimized -ArgumentList "ollama serve"
Start-Process powershell -WindowStyle Minimized -ArgumentList "open-webui serve"
Start-Process "http://localhost:8080"