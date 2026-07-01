$liveLog = "C:\App\AI\logs\transcript.log"
$backup = "C:\App\AI\logs\transcript.log.bak"
if (Test-Path $liveLog) { Move-Item $liveLog $backup -Force }

@"
2026-07-01T01:30:00 USER: jarvis what time is it
2026-07-01T01:30:00 [time] JARVIS: The current time is 01:30.
2026-07-01T01:32:30 RATING: +1 good
2026-07-01T01:31:00 USER: jarvis tell me a joke
2026-07-01T01:31:00 [joke] JARVIS: Why did the AI cross the road?
2026-07-01T01:32:45 RATING: +2 hilarious
2026-07-01T01:33:00 RATING: +1 yes
2026-07-01T01:34:00 USER: my favorite color is teal
2026-07-01T01:34:00 [llm] JARVIS: Got it, teal.
2026-07-01T01:35:00 RATING: -1 wrong
"@ | Set-Content -Path $liveLog -Encoding UTF8

# Manually inline the export logic.
$rows = New-Object System.Collections.Generic.List[object]
$lastJarvis = $null
foreach ($line in Get-Content $liveLog) {
    if ($line -match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\s+(\[\w+\]\s+)?JARVIS:\s+(.*)$') {
        $ts = ($line -split ' ')[0]
        $lastJarvis = @{ ts = $ts; text = $Matches[2] }
    } elseif ($line -match 'RATING:\s+([+-]?\d+)\s*(.*)$' -and $null -ne $lastJarvis) {
        $val = [int]$Matches[1]
        $comment = $Matches[2].Trim()
        $rows.Add([pscustomobject]@{
            Timestamp = $lastJarvis.ts
            Rating = $val
            Comment = $comment
            JarvisText = $lastJarvis.text
        })
        $lastJarvis = $null
    }
}
Write-Host ("In-memory rows: " + $rows.Count)
$rows | Format-Table -AutoSize

# Now actually run the control center function.
$source = Get-Content "C:\App\AI\scripts\Jarvis-ControlCenter.ps1" -Raw
$trimmed = $source -replace 'while \(\$true\) \{[\s\S]*?\}\s*$', ''
Invoke-Expression $trimmed

$testCsv = "C:\App\AI\data\ratings_test.csv"
if (Test-Path $testCsv) { Remove-Item $testCsv -Force }
Export-RatingsToCsv 6>&1 | Out-Null
if (Test-Path $testCsv) {
    Write-Host ""
    Write-Host "--- CSV file content ---"
    Get-Content $testCsv
    Write-Host "--- Import-Csv count ---"
    $csv = Import-Csv $testCsv
    Write-Host ("Imported rows: " + $csv.Count)
    $csv | Format-Table -AutoSize
    Remove-Item $testCsv -Force
}

# Cleanup.
Remove-Item $liveLog -Force -ErrorAction SilentlyContinue
if (Test-Path $backup) { Move-Item $backup $liveLog -Force }
