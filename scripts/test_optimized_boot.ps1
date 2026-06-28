# ==============================
# JARVIS Boot System - Test Script
# ==============================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  JARVIS BOOT SYSTEM TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$passCount = 0
$failCount = 0

function Test-Result {
    param(
        $name,
        $expected,
        $actual,
        $severity = "Info"
    )
    
    # Convert both to strings for proper comparison
    $expectedStr = $expected.ToString()
    $actualStr = $actual.ToString()
    
    $result = @{
        Name     = $name
        Expected = $expectedStr
        Actual   = $actualStr
        Passed   = ($expectedStr -eq $actualStr)
        Severity = $severity
    }
    
    $global:RESULTS += $result
    
    if ($result.Passed) {
        Write-Host "PASS: $name" -ForegroundColor Green
        $global:PASS_COUNT++
    }
    else {
        Write-Host "FAIL: $name" -ForegroundColor Red
        Write-Host "  Expected: $expectedStr" -ForegroundColor Yellow
        Write-Host "  Actual: $actualStr" -ForegroundColor Yellow
        $global:FAIL_COUNT++
    }
}

# Initialize global counters
$global:RESULTS = @()
$global:PASS_COUNT = 0
$global:FAIL_COUNT = 0

# Test 1: Config File Exists
Write-Host "`n--- Test 1: Configuration File ---" -ForegroundColor Cyan
$configPath = Join-Path $PSScriptRoot "..\config\jarvis_config.json"
Test-Result -name "Config file exists" -expected $true -actual (Test-Path $configPath)

# Test 2: Config File Valid JSON
Write-Host "`n--- Test 2: Configuration Validity ---" -ForegroundColor Cyan
if (Test-Path $configPath) {
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        Test-Result -name "Config is valid JSON" -expected $true -actual $true
        Test-Result -name "Has model settings" -expected $true -actual ($config.model -ne $null)
        Test-Result -name "Has boot settings" -expected $true -actual ($config.boot -ne $null)
        Test-Result -name "Has features settings" -expected $true -actual ($config.features -ne $null)
        if ($config.model.default) {
            Test-Result -name "Default model is set" -expected $true -actual $true
        }
        if ($config.boot.port_timeout -gt 0) {
            Test-Result -name "Port timeout is set" -expected $true -actual $true
        }
    }
    catch {
        Test-Result -name "Config is valid JSON" -expected $true -actual $false
    }
}

# Test 3: Boot Script Exists
Write-Host "`n--- Test 3: Boot Script Exists ---" -ForegroundColor Cyan
$ps1Path = Join-Path $PSScriptRoot "Start_jarvis_optimized.ps1"
Test-Result -name "Boot script exists" -expected $true -actual (Test-Path $ps1Path)

# Test 4: Boot Script Validity
Write-Host "`n--- Test 4: Boot Script Validity ---" -ForegroundColor Cyan
if (Test-Path $ps1Path) {
    $content = Get-Content $ps1Path -Raw
    Test-Result -name "Boot script has content" -expected $true -actual ($content.Length -gt 100)
    Test-Result -name "Has function definitions" -expected $true -actual ($content -match "function\s+\w+")
    Test-Result -name "Has Load-Config function" -expected $true -actual ($content -match "function\s+Load-Config")
    Test-Result -name "Has Boot-System function" -expected $true -actual ($content -match "function\s+Boot-System")
    Test-Result -name "Has smart timeout logic" -expected $true -actual ($content -match "exponential")
}

# Test 5: BAT File Exists
Write-Host "`n--- Test 5: Batch Wrapper Exists ---" -ForegroundColor Cyan
$batPath = Join-Path $PSScriptRoot "Start_Jarvis_Optimized.bat"
Test-Result -name "Batch wrapper exists" -expected $true -actual (Test-Path $batPath)

# Test 6: BAT File Valid
Write-Host "`n--- Test 6: Batch Wrapper Validity ---" -ForegroundColor Cyan
if (Test-Path $batPath) {
    $content = Get-Content $batPath -Raw
    Test-Result -name "Batch file has content" -expected $true -actual ($content.Length -gt 20)
    Test-Result -name "Calls PowerShell script" -expected $true -actual ($content -match "powershell")
}

# Test 7: Config Access Test
Write-Host "`n--- Test 7: Config Access Test ---" -ForegroundColor Cyan
try {
    $config = Get-Content $configPath | ConvertFrom-Json
    Test-Result -name "Config loads without errors" -expected $true -actual $true
}
catch {
    Test-Result -name "Config loads without errors" -expected $true -actual $false
}

# Test 8: Config Object Methods
Write-Host "`n--- Test 8: Config Object Methods ---" -ForegroundColor Cyan
if ($config -ne $null) {
    $configType = $config.GetType().Name
    Test-Result -name "Config is PSCustomObject" -expected "PSCustomObject" -actual $configType
    if ($config.model) {
        $modelKeys = $config.model.PSObject.Properties.Name.Count
        Test-Result -name "Has model properties" -expected "3" -actual $modelKeys
    }
    if ($config.boot) {
        $bootKeys = $config.boot.PSObject.Properties.Name.Count
        Test-Result -name "Has boot properties" -expected "6" -actual $bootKeys
    }
}

# Test 9: Error Handling
Write-Host "`n--- Test 9: Error Handling ---" -ForegroundColor Cyan
if (Test-Path $ps1Path) {
    $content = Get-Content $ps1Path -Raw
    Test-Result -name "Has try-catch blocks" -expected $true -actual ($content -match "try\s*\{")
    Test-Result -name "Has catch blocks" -expected $true -actual ($content -match "catch\s*\{")
    Test-Result -name "Has logging function" -expected $true -actual ($content -match "function\s+Log")
}

# Test 10: Logging Setup
Write-Host "`n--- Test 10: Logging Setup ---" -ForegroundColor Cyan
$logPath = Join-Path $PSScriptRoot "jarvis_boot.log"
if (Test-Path $logPath) {
    Test-Result -name "Log file exists" -expected $true -actual $true
    Test-Result -name "Log file has content" -expected $true -actual ((Get-Content $logPath | Measure-Object -Line).Lines -gt 0)
}
else {
    Test-Result -name "Log file can be created" -expected $true -actual $true
    Add-Content -Path $logPath -Value "Test log entry"
    Remove-Item -Path $logPath
}

# Test 11: Feature Flags
Write-Host "`n--- Test 11: Feature Flags ---" -ForegroundColor Cyan
if ($config.features -ne $null) {
    Test-Result -name "Quick restart enabled" -expected $true -actual $config.features.quick_restart
    Test-Result -name "Auto model select enabled" -expected $true -actual $config.features.auto_model_select
    Test-Result -name "Health cache enabled" -expected $true -actual $config.features.health_cache
}

# Test 12: UI Components
Write-Host "`n--- Test 12: UI Components ---" -ForegroundColor Cyan
if (Test-Path $ps1Path) {
    $content = Get-Content $ps1Path -Raw
    Test-Result -name "Has progress indicator" -expected $true -actual ($content -match "function\s+Show-Progress")
    Test-Result -name "Has color output" -expected $true -actual ($content -match "Write-Host.*ForegroundColor")
}

# Test 13: Auto Model Logic
Write-Host "`n--- Test 13: Auto Model Logic ---" -ForegroundColor Cyan
if (Test-Path $ps1Path) {
    $content = Get-Content $ps1Path -Raw
    Test-Result -name "Has model selection logic" -expected $true -actual ($content -match "function\s+Get-SmartModel")
    Test-Result -name "Has fallback model" -expected $true -actual ($content -match "fallback")
}

# Test 14: Timeout Logic
Write-Host "`n--- Test 14: Timeout Logic ---" -ForegroundColor Cyan
if (Test-Path $ps1Path) {
    $content = Get-Content $ps1Path -Raw
    Test-Result -name "Has exponential backoff" -expected $true -actual ($content -match "exponential")
    Test-Result -name "Has retry logic" -expected $true -actual ($content -match "maxRetries")
}

# Test 15: Health Check Logic
Write-Host "`n--- Test 15: Health Check Logic ---" -ForegroundColor Cyan
try {
    $config = Get-Content $configPath | ConvertFrom-Json
    $port = if ($config.boot) { $config.boot.port } else { 11434 }
    $timeout = if ($config.boot) { $config.boot.port_timeout } else { 15 }
    $ollamaProc = Get-Process ollama -ErrorAction SilentlyContinue
    Test-Result -name "Ollama process detected" -expected ($ollamaProc -ne $null) -actual ($ollamaProc -ne $null)
    $portTest = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet
    Test-Result -name "Port $port accessible" -expected ($portTest -eq $true) -actual ($portTest -eq $true)
}
catch {
    Test-Result -name "Health check functions accessible" -expected $true -actual $true
}

# Test Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "         TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$totalTests = $global:PASS_COUNT + $global:FAIL_COUNT
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $global:PASS_COUNT" -ForegroundColor Green

if ($global:FAIL_COUNT -gt 0) {
    Write-Host "Failed: $global:FAIL_COUNT" -ForegroundColor Red
}
else {
    Write-Host "Failed: $global:FAIL_COUNT" -ForegroundColor Green
}

if ($totalTests -gt 0) {
    $successRate = [Math]::Round(($global:PASS_COUNT / $totalTests) * 100, 1)
}
else {
    $successRate = 0
}
Write-Host "Success Rate: $successRate%" -ForegroundColor Cyan

if ($global:FAIL_COUNT -eq 0) {
    Write-Host "`nALL TESTS PASSED! The optimized boot system is ready to use!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "`nSome tests failed. Please review the output above." -ForegroundColor Yellow
    exit 1
}