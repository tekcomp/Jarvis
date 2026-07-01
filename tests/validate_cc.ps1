$tokens = $null
$errs = $null
[System.Management.Automation.Language.Parser]::ParseFile('C:\App\AI\scripts\Jarvis-ControlCenter.ps1', [ref]$tokens, [ref]$errs) | Out-Null
if ($errs) {
    Write-Host "PARSE ERRORS:" -ForegroundColor Red
    $errs | Format-List
    exit 1
} else {
    Write-Host "OK: control center parses cleanly" -ForegroundColor Green
}
