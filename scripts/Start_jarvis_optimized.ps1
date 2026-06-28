# ==============================
# JARVIS BOOT SYSTEM - OPTIMIZED
# ==============================

$logFile = "$PSScriptRoot\jarvis_boot.log"

# ---- LOG SETUP ----
function Log($msg, $color = "White", $log = $true) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    if ($log) {
        Add-Content -Path $logFile -Value $line
    }
    if ($useColors -and $msg -ne "") {
        Write-Host $msg -ForegroundColor $color
    }
}

function Load-Config {
    $configPath = Join-Path $PSScriptRoot "..\config\jarvis_config.json"
    if (Test-Path $configPath) {
        try {
            return Get-Content $configPath | ConvertFrom-Json
        }
        catch {
            Write-Host "Warning: Config file corrupted, using defaults" -ForegroundColor Yellow
        }
    }
    return $null
}

function Get-ModelList {
    param($config)
    
    try {
        $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -UseBasicParsing -TimeoutSec 3
        return $tags.models
    }
    catch {
        Write-Host "Warning: Could not fetch model list" -ForegroundColor Yellow
        return @()
    }
}

function Get-SmartModel {
    param($config)
    
    $models = Get-ModelList -config $config
    
    # Priority 1: Gemma 3 models (optimized for voice assistance)
    $gemmaModels = $models | Where-Object { $_.name -like "gemma3:*" } | 
    Sort-Object { [double]($_.details.parameter_size) } -Descending | 
    Select-Object -First 1
    if ($gemmaModels) {
        Write-Host "Found Gemma 3 model: $($gemmaModels.name)" -ForegroundColor Cyan
        return $gemmaModels.name
    }
    
    # Priority 2: Llama 3.1 models (general voice assistant)
    $llamaModels = $models | Where-Object { $_.name -like "llama3.1:*" } | 
    Sort-Object { [double]($_.details.parameter_size) } -Descending | 
    Select-Object -First 1
    if ($llamaModels) {
        Write-Host "Found Llama 3.1 model: $($llamaModels.name)" -ForegroundColor Cyan
        return $llamaModels.name
    }
    
    # Priority 3: Qwen 2.5 models (balanced performance)
    $qwenModels = $models | Where-Object { $_.name -like "qwen2.5:*" } | 
    Sort-Object { [double]($_.details.parameter_size) } -Descending | 
    Select-Object -First 1
    if ($qwenModels) {
        Write-Host "Found Qwen 2.5 model: $($qwenModels.name)" -ForegroundColor Cyan
        return $qwenModels.name
    }
    
    # Priority 4: Coding model (qwen2.5-coder)
    $codingModel = $models | Where-Object { $_.name -like "qwen2.5-coder*" } | Select-Object -First 1
    if ($codingModel) {
        Write-Host "Found coding model: $($codingModel.name)" -ForegroundColor Cyan
        return $codingModel.name
    }
    
    # Priority 5: Large models (for general use)
    $largeModels = $models | Where-Object { $_.details.parameter_size -match "14|29" } | 
    Sort-Object { [double]($_.details.parameter_size) } -Descending | 
    Select-Object -First 1
    
    if ($largeModels) {
        Write-Host "Found large model: $($largeModels.name)" -ForegroundColor Cyan
        return $largeModels.name
    }
    
    # Priority 6: Default from config
    if ($config.features.auto_model_select -and $config.model.home_voice.default) {
        Write-Host "Auto-selecting default home voice model..." -ForegroundColor Cyan
        return $config.model.home_voice.default
    }
    
    # Priority 7: Coding default
    if ($config.features.auto_model_select -and $config.model.coding.default) {
        Write-Host "Auto-selecting default coding model..." -ForegroundColor Cyan
        return $config.model.coding.default
    }
    
    # Priority 8: First available model
    if ($models -and $models.Count -gt 0) {
        Write-Host "Using first available model: $($models[0].name)" -ForegroundColor Cyan
        return $models[0].name
    }
    
    # Last resort: glm-4.7-flash
    Write-Host "Using glm-4.7-flash as fallback..." -ForegroundColor Yellow
    return "glm-4.7-flash:latest"
}

function Test-OllamaAPI {
    param($config)
    
    $maxRetries = if ($config.performance) { $config.performance.max_retries } else { 2 }
    $retryDelay = 2
    
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $timeout = if ($config.boot) { $config.boot.api_timeout } else { 2 }
            Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec $timeout | Out-Null
            return $true
        }
        catch {
            if ($i -lt $maxRetries) {
                Start-Sleep -Seconds $retryDelay
                $retryDelay = [Math]::Min($retryDelay * 2, 5)  # Exponential backoff
            }
        }
    }
    return $false
}

function Get-PortStatus {
    param($config)
    
    $port = if ($config.boot) { $config.boot.port } else { 11434 }
    $timeout = if ($config.boot) { $config.boot.port_timeout } else { 15 }
    $interval = if ($config.boot) { $config.boot.port_check_interval } else { 2 }
    
    $endTime = (Get-Date).AddSeconds($timeout)
    
    while ((Get-Date) -lt $endTime) {
        if (Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet) {
            return $true
        }
        Start-Sleep -Seconds $interval
    }
    return $false
}

function Show-Progress {
    param(
        $message,
        $totalSteps,
        $stepNumber,
        $color = "Cyan"
    )
    
    if ($showProgress) {
        $percent = [Math]::Round(($stepNumber / $totalSteps) * 100, 0)
        Write-Host "`r$message... $percent% [OK]" -ForegroundColor $color -NoNewline
    }
}

function Boot-System {
    param($config)
    
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "     JARVIS BOOT SYSTEM" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Log "Boot sequence started" "Cyan"
    
    # Step 1: Check Ollama Process
    Show-Progress "Checking Ollama process" 4 1
    
    $ollamaProc = Get-Process ollama -ErrorAction SilentlyContinue
    
    if ($ollamaProc -eq $null) {
        Log "Ollama not running. Starting..." "Yellow"
        Start-Process "ollama" -ArgumentList "serve"
        Start-Sleep -Seconds 4
    }
    else {
        Log "Ollama running (PID $($ollamaProc.Id))" "Green"
    }
    
    # Step 2: Port Check
    Show-Progress "Waiting for port 11434" 4 2
    
    $portReady = Get-PortStatus -config $config
    
    if (-not $portReady) {
        Log "Port failed. Restarting Ollama..." "Red"
        
        Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Start-Process "ollama" -ArgumentList "serve"
        Start-Sleep -Seconds 5
        
        $portReady = Get-PortStatus -config $config
        if (-not $portReady) {
            Log "FATAL: Port check still failed" "Red"
            exit 1
        }
    }
    
    Log "Port 11434 is open OK" "Green"
    
    # Step 3: API Check
    Show-Progress "Checking API health" 4 3
    
    $apiReady = Test-OllamaAPI -config $config
    
    if (-not $apiReady) {
        Log "FATAL: API not responding" "Red"
        exit 1
    }
    
    Log "API responding OK" "Green"
    
    # Step 4: Model Warmup
    Show-Progress "Warming up model" 4 4
    
    $model = Get-SmartModel -config $config
    Log "Model selected: $model" "Green"
    
    $body = @{
        model  = $model
        prompt = "Respond with OK only"
        stream = $false
    } | ConvertTo-Json -Depth 3
    
    $timeout = if ($config.boot) { $config.boot.warmup_timeout } else { 30 }
    
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method POST -Body $body -ContentType "application/json" -TimeoutSec $timeout | Out-Null
        Log "Model warmup successful" "Green"
    }
    catch {
        Log "Model warmup failed" "Red"
        exit 1
    }
    
    # Completion
    Write-Host "`r"  # Clear progress bar
    Write-Host ""
    Log "JARVIS READY SYSTEM ONLINE" "Green"
    Log "Launching Jarvis chat with $model"
    
    # Start Chat
    if ($config.features.quick_restart -and $config.features.health_cache) {
        # Quick restart with cached model
        ollama run $model
    }
    else {
        # Full restart
        Start-Process "ollama" -ArgumentList "run $model"
    }
}

# Load Configuration
$config = Load-Config
$useColors = if ($config -and $config.ui -and $config.ui.use_colors) { $config.ui.use_colors } else { $true }
$showProgress = if ($config -and $config.ui -and $config.ui.show_progress) { $config.ui.show_progress } else { $true }

# Start Boot Sequence
Boot-System -config $config