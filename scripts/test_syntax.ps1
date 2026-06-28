$syntaxErrors = $null
$tokens = [System.Management.Automation.PSParser]::Tokenize((Get-Content 'f:\media\Projects\JarvisAi\scripts\Start_jarvis.ps1' -Raw), [ref]$syntaxErrors)

if ($syntaxErrors) {
    foreach ($e in $syntaxErrors) {
        Write-Host "Line $($e.LineNumber): $($e.Message)"
        Write-Host "Text: $($e.Content)"
    }
}
else {
    Write-Host "No syntax errors found!"
}