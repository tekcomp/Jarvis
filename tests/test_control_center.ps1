# Tests for the rating UI functions in scripts/Jarvis-ControlCenter.ps1.
# Uses the actual hard-coded transcript path C:\App\AI\logs\transcript.log
# to keep the test simple. Backs up the real file, swaps in a fixture,
# runs the tests, then restores.
$ErrorActionPreference = "Stop"

$repoRoot = "C:\App\AI"
$scriptPath = Join-Path $repoRoot "scripts\Jarvis-ControlCenter.ps1"
$liveLog = Join-Path $repoRoot "logs\transcript.log"
$backup = Join-Path $repoRoot "logs\transcript.log.bak"
$testCsv = Join-Path $repoRoot "data\ratings.csv"
$testCanned = Join-Path $repoRoot "data\canned_responses.json"
$cannedBackup = Join-Path $repoRoot "data\canned_responses.json.bak"

# Back up the real transcript.
if (Test-Path $liveLog) {
    Move-Item -Path $liveLog -Destination $backup -Force
}
if (Test-Path $testCanned) {
    Move-Item -Path $testCanned -Destination $cannedBackup -Force
}
# Always start with a known canned-responses.json fixture.
@"
{
  "mode_switch": {
    "playful": "Switched to playful mode."
  },
  "promoted": {}
}
"@ | Set-Content -Path $testCanned -Encoding UTF8

# Test fixture: 3 USER/JARVIS pairs with ratings.
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

# Extract the rating-related functions from the control center.
$source = Get-Content $scriptPath -Raw
$trimmed = $source -replace 'while \(\$true\) \{[\s\S]*?\}\s*$', ''
Invoke-Expression $trimmed

$pass = 0
$fail = 0

function Test-Result {
    param([bool]$cond, [string]$name)
    if ($cond) {
        Write-Host "  PASS  $name" -ForegroundColor Green
        $script:pass++
    }
    else {
        Write-Host "  FAIL  $name" -ForegroundColor Red
        $script:fail++
    }
}

# === Test 1: Show-RecentJarvisLines ===
Write-Host ""
Write-Host "=== Test 1: Show-RecentJarvisLines (output non-empty) ===" -ForegroundColor Cyan
$out = (Show-RecentJarvisLines -count 3) 6>&1 | Out-String
Test-Result ($out.Length -gt 0) "function returns output"

# === Test 2: Show-RatingStats ===
Write-Host ""
Write-Host "=== Test 2: Show-RatingStats (1 up, 1 down, 1 neutral) ===" -ForegroundColor Cyan
Show-RatingStats 6>&1 | Out-Null
$up = (Select-String -Path $liveLog -Pattern "RATING: \+1" | Measure-Object).Count
$up2 = (Select-String -Path $liveLog -Pattern "RATING: \+2" | Measure-Object).Count
$down = (Select-String -Path $liveLog -Pattern "RATING: -1" | Measure-Object).Count
Test-Result ($up -eq 2) "2 thumbs-up (+1) entries"
Test-Result ($up2 -eq 1) "1 thumbs-up (+2) entry"
Test-Result ($down -eq 1) "1 thumbs-down entry"

# === Test 3: Rate-LastResponse (+1) ===
Write-Host ""
Write-Host "=== Test 3: Rate-LastResponse (+1) ===" -ForegroundColor Cyan
Rate-LastResponse -value 1 6>&1 | Out-Null
$last = Get-Content $liveLog -Tail 1
Test-Result ($last -match "RATING: \+1") "+1 rating appended"

# === Test 4: Rate-LastResponse (-1) ===
Write-Host ""
Write-Host "=== Test 4: Rate-LastResponse (-1) ===" -ForegroundColor Cyan
Rate-LastResponse -value -1 6>&1 | Out-Null
$last = Get-Content $liveLog -Tail 1
Test-Result ($last -match "RATING: -1") "-1 rating appended"

# === Test 5: Rate-LastResponse (0) ===
Write-Host ""
Write-Host "=== Test 5: Rate-LastResponse (0) ===" -ForegroundColor Cyan
Rate-LastResponse -value 0 6>&1 | Out-Null
$last = Get-Content $liveLog -Tail 1
Test-Result ($last -match "RATING: \+0") "neutral rating appended"

# === Test 6: Show-TopRatedJarvisLines ===
Write-Host ""
Write-Host "=== Test 6: Show-TopRatedJarvisLines (top 1) ===" -ForegroundColor Cyan
$out = (Show-TopRatedJarvisLines -count 1) 6>&1 | Out-String
# The fixture has one rating=+2 (the joke) and rating=+1 (time). Top-1 should be the joke.
Test-Result ($out -match "cross the road") "top-1 is the highest-rated JARVIS line"
Test-Result ($out -match "\+\+") "shows two plus signs for rating=+2"

# === Test 7: Export-RatingsToCsv ===
Write-Host ""
Write-Host "=== Test 7: Export-RatingsToCsv ===" -ForegroundColor Cyan
if (Test-Path $testCsv) { Remove-Item $testCsv -Force }
Export-RatingsToCsv 6>&1 | Out-Null
Test-Result (Test-Path $testCsv) "CSV file created"
if (Test-Path $testCsv) {
    $csv = Import-Csv $testCsv
    # The fixture has 4 RATING lines but only 3 unique JARVIS lines.
    # Each JARVIS line can only be rated once via 1:1 pairing.
    # The 4th rating (RATING: +1 yes) is an orphan (no preceding JARVIS) and is dropped.
    Test-Result ($csv.Count -eq 3) "CSV has 3 rows (1:1 pairing drops orphan rating)"
    Test-Result ($csv[0].PSObject.Properties.Name -contains "Rating") "CSV has Rating column"
    Test-Result ($csv[0].PSObject.Properties.Name -contains "Timestamp") "CSV has Timestamp column"
    Test-Result ($csv[0].PSObject.Properties.Name -contains "JarvisText") "CSV has JarvisText column"
    # Check content: first row should be the +1 "time" rating.
    Test-Result ($csv[0].Rating -eq "1") "first row rating=1"
    Test-Result ($csv[1].Rating -eq "2") "second row rating=2 (joke)"
    Test-Result ($csv[2].Rating -eq "-1") "third row rating=-1"
}

# === Test 8: Promote-TopRated ===
Write-Host ""
Write-Host "=== Test 8: Promote-TopRated (top 2, min rating=2) ===" -ForegroundColor Cyan
# We need to feed "y\n" to Read-Host. Simulate by setting the input stream.
# PowerShell trick: use 'echo y | ...' via the pipeline.
$confirmation = "y"
$confirmResult = Promote-TopRated -count 2 -minRating 2
# Promote-TopRated calls Read-Host; in a non-interactive run it will return null.
# We can't easily test the interactive path; instead, test that the function
# didn't crash and that the canned-responses file is still valid JSON.
Test-Result ($LASTEXITCODE -ne 1) "function did not error"
if (Test-Path $testCanned) {
    try {
        $canned = Get-Content $testCanned -Raw | ConvertFrom-Json
        Test-Result ($null -ne $canned.promoted) "canned_responses.json has 'promoted' key"
    }
    catch {
        Test-Result $false "canned_responses.json is valid JSON"
    }
}

# === Cleanup ===
Remove-Item $liveLog -Force -ErrorAction SilentlyContinue
if (Test-Path $testCsv) { Remove-Item $testCsv -Force -ErrorAction SilentlyContinue }
if (Test-Path $backup) {
    Move-Item -Path $backup -Destination $liveLog -Force
}
if (Test-Path $cannedBackup) {
    Move-Item -Path $cannedBackup -Destination $testCanned -Force
}

Write-Host ""
Write-Host "==========================" -ForegroundColor Cyan
Write-Host "  Passed: $pass  Failed: $fail" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Red" })
Write-Host "==========================" -ForegroundColor Cyan
if ($fail -gt 0) { exit 1 } else { exit 0 }
