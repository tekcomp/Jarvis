# ============================================================
# JARVIS CONTROL CENTER
# Version 2.1 - With Multi-Level Logging + Graceful Kill
# ============================================================

# ============================================================
# CONFIGURATION
# ============================================================
$JarvisPath = "$env:USERPROFILE\Jarvis"
$LogPath = "C:\App\Ai\logs\logs.txt"
$LogLevel = "NORMAL" # Options: VERBOSE, NORMAL, QUIET
$OllamaExe = "ollama.exe" # Ensure 'ollama' is in your PATH or provide full path

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Log {
    param([string]$message, [string]$level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$level] $message"
    
    # Write to console based on level
    switch ($level) {
        "DEBUG" { if ($LogLevel -eq "VERBOSE") { Write-Host $logEntry -ForegroundColor DarkGray } }
        "INFO" { if ($LogLevel -ne "QUIET") { Write-Host $logEntry -ForegroundColor Cyan } }
        "WARN" { if ($LogLevel -ne "QUIET") { Write-Host $logEntry -ForegroundColor Yellow } }
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
    }

    # Write to file
    Add-Content -Path $LogPath -Value $logEntry
}

function Get-VoiceAssistantStatus {
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($proc) { return "Running" }
    return "Stopped"
}

function Wait-Jarvis {
    param([int]$seconds = 2)
    Start-Sleep -Seconds $seconds
}

function Show-LogFile {
    if (Test-Path $LogPath) {
        Get-Content $LogPath | Select-Object -Last 50
    }
    else {
        Write-Host "Log file not found." -ForegroundColor Yellow
    }
}

function Clear-LogFile {
    if (Test-Path $LogPath) {
        Remove-Item $LogPath
        Write-Host "Log cleared." -ForegroundColor Green
    }
}

function Set-LogLevel {
    param([string]$level)
    $validLevels = @("VERBOSE", "NORMAL", "QUIET")
    if ($level -in $validLevels) {
        $global:LogLevel = $level
        Write-Host "Log level set to: $level" -ForegroundColor Green
    }
    else {
        Write-Host "Invalid level. Use VERBOSE, NORMAL, or QUIET." -ForegroundColor Red
    }
}

function Launch-Model {
    param([string]$model)
    Write-Host "Launching model: $model" -ForegroundColor Cyan
    Start-Process -FilePath "ollama" -ArgumentList "run $model"
}

# ============================================================
# MAIN FUNCTIONS
# ============================================================

function Start-VoiceAssistant {
    Write-Host "Starting JARVIS..." -ForegroundColor Green
    Log "Starting JARVIS..."
    
    # Check if python is installed
    $pythonCheck = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCheck) {
        Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
        Log "Error: Python not found."
        return
    }

    # Start the main script
    Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Normal
}

function Stop-VoiceAssistant {
    Write-Host "Stopping JARVIS..." -ForegroundColor Yellow
    Log "Stopping JARVIS..."
    
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    
    if ($proc) {
        # Try graceful shutdown first (writing to file)
        $stopFile = "$JarvisPath\stop_signal.txt"
        Set-Content -Path $stopFile -Value "shutdown"
        
        # Wait a moment for graceful exit
        Start-Sleep -Seconds 2
        
        # Force kill if still running
        if ($proc) {
            Write-Host "Force killing Python process..." -ForegroundColor Red
            $proc | Stop-Process -Force
        }
        Write-Host "JARVIS stopped." -ForegroundColor Green
    }
    else {
        Write-Host "JARVIS is not running." -ForegroundColor Yellow
    }
}

function Stop-VoiceAssistantGracefully {
    Write-Host "Sending graceful shutdown signal..." -ForegroundColor Yellow
    Log "Sending graceful shutdown signal..."
    
    $stopFile = "$JarvisPath\stop_signal.txt"
    Set-Content -Path $stopFile -Value "shutdown"
    
    # Wait for the process to read the file and exit
    Start-Sleep -Seconds 3
    Write-Host "Signal sent." -ForegroundColor Green
}

# ============================================================
# RATING UI
# ============================================================
# Lets the user rate past JARVIS responses visually. Backed by
# tools/rate_jarvis.py (which appends a RATING: line to
# logs/transcript.log) and tools/transcript_filter.py (which lists
# recent JARVIS lines). Also offers top-N best responses, a CSV
# export, and a "promote" action that copies a highly-rated JARVIS
# line into data/canned_responses.json for future use.
$TranscriptLog = "C:\App\AI\logs\transcript.log"
$CannedResponsesPath = "C:\App\AI\data\canned_responses.json"
$RatingsCsv = "C:\App\AI\data\ratings.csv"
$PromotedBucket = "promoted"   # key in canned_responses.json where promoted lines go

function Show-RecentJarvisLines {
    param([int]$count = 5)
    if (-not (Test-Path $TranscriptLog)) {
        Write-Host "No transcript.log found at $TranscriptLog" -ForegroundColor Yellow
        return
    }
    # Pull the last N JARVIS lines (skip RATING: lines which also start with a ts).
    $lines = Get-Content $TranscriptLog -Tail 400 |
    Where-Object { $_ -match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*JARVIS:' } |
    Select-Object -Last $count
    if (-not $lines) {
        Write-Host "No JARVIS lines found in the transcript yet." -ForegroundColor Yellow
        return
    }
    Write-Host ""
    Write-Host "Recent JARVIS responses (most recent last):" -ForegroundColor Cyan
    Write-Host ("-" * 70) -ForegroundColor DarkGray
    $i = 0
    foreach ($line in $lines) {
        $i++
        # Strip the [intent] tag for readability.
        $clean = $line -replace '\[\w+\]\s*', ''
        if ($clean.Length -gt 90) { $clean = $clean.Substring(0, 87) + "..." }
        Write-Host ("  [{0}] {1}" -f $i, $clean) -ForegroundColor White
    }
    Write-Host ("-" * 70) -ForegroundColor DarkGray
}

function Show-TopRatedJarvisLines {
    # Find all JARVIS lines and their associated ratings, then rank by rating desc.
    param([int]$count = 5)
    if (-not (Test-Path $TranscriptLog)) {
        Write-Host "No transcript.log found at $TranscriptLog" -ForegroundColor Yellow
        return
    }
    $all = Get-Content $TranscriptLog
    $pairs = New-Object System.Collections.Generic.List[object]
    $lastJarvis = $null
    foreach ($line in $all) {
        if ($line -match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\s+(\[\w+\]\s+)?JARVIS:\s+(.*)$') {
            $lastJarvis = @{ ts = ($line -split ' ')[0]; text = $Matches[2] }
        }
        elseif ($line -match 'RATING:\s+([+-]?\d+)\s*(.*)$' -and $null -ne $lastJarvis) {
            $val = [int]$Matches[1]
            if ($val -gt 0) {
                $pairs.Add([pscustomobject]@{
                        Rating    = $val
                        Timestamp = $lastJarvis.ts
                        Text      = $lastJarvis.text
                    })
            }
            $lastJarvis = $null
        }
    }
    if ($pairs.Count -eq 0) {
        Write-Host "No rated JARVIS lines yet. Try option [9] to rate a response." -ForegroundColor Yellow
        return
    }
    $top = $pairs | Sort-Object -Property @{Expression = "Rating"; Descending = $true }, @{Expression = "Timestamp"; Descending = $true } | Select-Object -First $count
    Write-Host ""
    Write-Host ("Top {0} rated JARVIS responses:" -f $top.Count) -ForegroundColor Cyan
    Write-Host ("-" * 70) -ForegroundColor DarkGray
    $i = 0
    foreach ($p in $top) {
        $i++
        $short = $p.Text
        if ($short.Length -gt 80) { $short = $short.Substring(0, 77) + "..." }
        $tag = "+" * $p.Rating
        Write-Host ("  [{0}] {1} {2}  ({3})" -f $i, $tag, $short, $p.Timestamp) -ForegroundColor Green
    }
    Write-Host ("-" * 70) -ForegroundColor DarkGray
}

function Rate-LastResponse {
    param([int]$value)
    $tool = "C:\App\AI\tools\rate_jarvis.py"
    if (-not (Test-Path $tool)) {
        Write-Host "rate_jarvis.py not found at $tool" -ForegroundColor Red
        return
    }
    $label = @{ 1 = "thumbs up"; 0 = "neutral"; -1 = "thumbs down" }[$value]
    Write-Host "Recording $label (rating=$value)..." -ForegroundColor Cyan
    & python $tool --value $value
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Done." -ForegroundColor Green
    }
    else {
        Write-Host "Failed to record rating." -ForegroundColor Red
    }
}

function Rate-ByTime {
    param([string]$hhmm)
    $tool = "C:\App\AI\tools\rate_jarvis.py"
    if (-not (Test-Path $tool)) {
        Write-Host "rate_jarvis.py not found at $tool" -ForegroundColor Red
        return
    }
    $value = Read-Host "  Rating for that response (-1 / 0 / +1)"
    try {
        $v = [int]$value
    }
    catch {
        Write-Host "Invalid rating." -ForegroundColor Red
        return
    }
    & python $tool --ts $hhmm --value $v
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Done." -ForegroundColor Green
    }
    else {
        Write-Host "Failed to record rating." -ForegroundColor Red
    }
}

function Show-RatingStats {
    if (-not (Test-Path $TranscriptLog)) {
        Write-Host "No transcript.log found at $TranscriptLog" -ForegroundColor Yellow
        return
    }
    $ratings = Get-Content $TranscriptLog | Where-Object { $_ -match 'RATING:\s+([+-]?\d+)' }
    $up = ($ratings | Where-Object { $_ -match 'RATING:\s+\+1' }).Count
    $down = ($ratings | Where-Object { $_ -match 'RATING:\s+-1' }).Count
    $neutral = ($ratings | Where-Object { $_ -match 'RATING:\s+\+?0' }).Count
    $total = $ratings.Count
    Write-Host ""
    Write-Host "Rating stats:" -ForegroundColor Cyan
    Write-Host ("  Thumbs up:    {0}" -f $up) -ForegroundColor Green
    Write-Host ("  Neutral:      {0}" -f $neutral) -ForegroundColor Gray
    Write-Host ("  Thumbs down:  {0}" -f $down) -ForegroundColor Red
    Write-Host ("  Total:        {0}" -f $total) -ForegroundColor White
    if ($total -gt 0) {
        $pct = [math]::Round(($up / $total) * 100, 1)
        Write-Host ("  Approval rate: {0}%" -f $pct) -ForegroundColor Cyan
    }
    Write-Host ""
}

function Export-RatingsToCsv {
    # Walk the transcript and pair each JARVIS line with the next
    # rating line. Write one CSV row per (JARVIS, rating) pair.
    if (-not (Test-Path $TranscriptLog)) {
        Write-Host "No transcript.log found at $TranscriptLog" -ForegroundColor Yellow
        return
    }
    $all = Get-Content $TranscriptLog
    $rows = New-Object System.Collections.Generic.List[object]
    $lastJarvis = $null
    foreach ($line in $all) {
        if ($line -match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\s+(\[\w+\]\s+)?JARVIS:\s+(.*)$') {
            $lastJarvis = @{
                ts   = ($line -split ' ')[0]
                text = $Matches[2]
            }
        }
        elseif ($line -match 'RATING:\s+([+-]?\d+)\s*(.*)$' -and $null -ne $lastJarvis) {
            $val = [int]$Matches[1]
            $comment = $Matches[2].Trim()
            $rows.Add([pscustomobject]@{
                    Timestamp  = $lastJarvis.ts
                    Rating     = $val
                    Comment    = $comment
                    JarvisText = $lastJarvis.text
                })
            $lastJarvis = $null
        }
    }
    if ($rows.Count -eq 0) {
        Write-Host "No ratings found. Use option [9]/[A]/[B] first." -ForegroundColor Yellow
        return
    }
    $dir = Split-Path $RatingsCsv -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $rows | Select-Object Timestamp, Rating, Comment, JarvisText |
    Export-Csv -Path $RatingsCsv -NoTypeInformation -Encoding UTF8
    Write-Host ("Wrote {0} row(s) to {1}" -f $rows.Count, $RatingsCsv) -ForegroundColor Green
}

function Promote-TopRated {
    # Copy the highest-rated JARVIS line into data/canned_responses.json
    # under a `promoted` bucket, so future runs can reuse it.
    param([int]$count = 3, [int]$minRating = 2)
    if (-not (Test-Path $TranscriptLog)) {
        Write-Host "No transcript.log found at $TranscriptLog" -ForegroundColor Yellow
        return
    }
    $all = Get-Content $TranscriptLog
    $candidates = New-Object System.Collections.Generic.List[object]
    $lastJarvis = $null
    foreach ($line in $all) {
        if ($line -match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\s+(\[\w+\]\s+)?JARVIS:\s+(.*)$') {
            $lastJarvis = @{
                ts   = ($line -split ' ')[0]
                text = $Matches[2]
            }
        }
        elseif ($line -match 'RATING:\s+([+-]?\d+)' -and $null -ne $lastJarvis) {
            $val = [int]$Matches[1]
            if ($val -ge $minRating) {
                $candidates.Add([pscustomobject]@{
                        Rating    = $val
                        Timestamp = $lastJarvis.ts
                        Text      = $lastJarvis.text
                    })
            }
            $lastJarvis = $null
        }
    }
    if ($candidates.Count -eq 0) {
        Write-Host "No JARVIS lines meet the min-rating threshold ($minRating)." -ForegroundColor Yellow
        return
    }
    $top = $candidates | Sort-Object -Property @{Expression = "Rating"; Descending = $true }, @{Expression = "Timestamp"; Descending = $true } | Select-Object -First $count

    # Load the canned-responses file.
    # ConvertFrom-Json returns PSCustomObject; nested objects are also
    # PSCustomObject, which is NOT indexable with []. Coerce each top-level
    # value to [ordered]@{} so we can $bucket[$key] = $value later.
    $canned = [ordered]@{}
    if (Test-Path $CannedResponsesPath) {
        $raw = Get-Content $CannedResponsesPath -Raw | ConvertFrom-Json
        if ($null -ne $raw) {
            foreach ($prop in $raw.PSObject.Properties) {
                $val = $prop.Value
                if ($val -is [System.Management.Automation.PSObject] -and $val -isnot [hashtable] -and $val -isnot [System.Collections.IDictionary]) {
                    $inner = [ordered]@{}
                    if ($val.PSObject.Properties) {
                        foreach ($p2 in $val.PSObject.Properties) { $inner[$p2.Name] = $p2.Value }
                    }
                    $val = $inner
                }
                $canned[$prop.Name] = $val
            }
        }
    }
    if (-not $canned.Contains($PromotedBucket)) {
        $canned[$PromotedBucket] = [ordered]@{}
    }
    $bucket = $canned[$PromotedBucket]

    Write-Host ""
    Write-Host ("Top {0} candidate(s) to promote:" -f $top.Count) -ForegroundColor Cyan
    $i = 0
    foreach ($c in $top) {
        $i++
        $short = $c.Text
        if ($short.Length -gt 80) { $short = $short.Substring(0, 77) + "..." }
        Write-Host ("  [{0}] rating={1}  {2}" -f $i, $c.Rating, $short) -ForegroundColor Green
    }
    $confirm = Read-Host "  Promote these to data/canned_responses.json under '$PromotedBucket'? (y/n)"
    if ($confirm -ne 'y') {
        Write-Host "Cancelled." -ForegroundColor Yellow
        return
    }

    # Each entry: key = "promoted_<n>", value = the JARVIS text.
    $i = 0
    foreach ($c in $top) {
        $i++
        $key = "promoted_$i"
        $bucket[$key] = $c.Text
    }
    # Convert hashtable back to PSCustomObject for JSON serialization.
    $obj = [pscustomobject]$canned
    $json = $obj | ConvertTo-Json -Depth 10
    $dir = Split-Path $CannedResponsesPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $CannedResponsesPath -Value $json -Encoding UTF8
    Write-Host ("Wrote {0} promoted line(s) to {1}" -f $top.Count, $CannedResponsesPath) -ForegroundColor Green
}

# ============================================================
# MENU LOOP
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   JARVIS CONTROL CENTER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

while ($true) {
    Write-Host ""
    Write-Host "  --- System ---" -ForegroundColor DarkCyan
    Write-Host "  [1] Start JARVIS" -ForegroundColor White
    Write-Host "  [2] Stop JARVIS (Force)" -ForegroundColor White
    Write-Host "  [3] Stop JARVIS (Graceful)" -ForegroundColor White
    Write-Host "  [4] Launch Ollama Model" -ForegroundColor White
    Write-Host ""
    Write-Host "  --- Logs ---" -ForegroundColor DarkCyan
    Write-Host "  [5] View Logs" -ForegroundColor White
    Write-Host "  [6] Clear Logs" -ForegroundColor White
    Write-Host "  [7] Set Log Level (VERBOSE/NORMAL/QUIET)" -ForegroundColor White
    Write-Host ""
    Write-Host "  --- Ratings ---" -ForegroundColor DarkCyan
    Write-Host "  [8] Show recent JARVIS responses" -ForegroundColor White
    Write-Host "  [9] Thumbs-up the last response" -ForegroundColor Green
    Write-Host "  [A] Thumbs-down the last response" -ForegroundColor Red
    Write-Host "  [B] Rate a specific response (by time)" -ForegroundColor White
    Write-Host "  [C] Show rating stats" -ForegroundColor White
    Write-Host "  [D] Top-rated JARVIS responses" -ForegroundColor White
    Write-Host "  [E] Export ratings to CSV" -ForegroundColor White
    Write-Host "  [F] Promote top-rated to canned_responses.json" -ForegroundColor White
    Write-Host ""
    Write-Host "  [0] Exit" -ForegroundColor White

    $choice = Read-Host "Please select an option"

    switch ($choice) {
        "1" { Start-VoiceAssistant }
        "2" { Stop-VoiceAssistant }
        "3" { Stop-VoiceAssistantGracefully }
        "4" {
            $model = Read-Host "Enter model name (e.g., llama2)"
            Launch-Model -model $model
        }
        "5" { Show-LogFile }
        "6" { Clear-LogFile }
        "7" {
            $level = Read-Host "Enter level (VERBOSE/NORMAL/QUIET)"
            Set-LogLevel -level $level
        }
        "8" {
            $n = Read-Host "How many recent JARVIS lines to show? (default 5)"
            if ([string]::IsNullOrWhiteSpace($n)) { $n = 5 }
            Show-RecentJarvisLines -count ([int]$n)
        }
        "9" { Rate-LastResponse -value 1 }
        "A" { Rate-LastResponse -value -1 }
        "B" {
            $t = Read-Host "Enter time of JARVIS response (HH:MM, today)"
            if ([string]::IsNullOrWhiteSpace($t)) {
                Write-Host "No time given." -ForegroundColor Yellow
            }
            else {
                Rate-ByTime -hhmm $t
            }
        }
        "C" { Show-RatingStats }
        "D" {
            $n = Read-Host "How many top-rated to show? (default 5)"
            if ([string]::IsNullOrWhiteSpace($n)) { $n = 5 }
            Show-TopRatedJarvisLines -count ([int]$n)
        }
        "E" { Export-RatingsToCsv }
        "F" {
            $n = Read-Host "How many to promote? (default 3)"
            $r = Read-Host "Minimum rating to include? (default 2)"
            if ([string]::IsNullOrWhiteSpace($n)) { $n = 3 }
            if ([string]::IsNullOrWhiteSpace($r)) { $r = 2 }
            Promote-TopRated -count ([int]$n) -minRating ([int]$r)
        }
        "0" {
            Write-Host "Exiting..." -ForegroundColor Yellow
            exit
        }
        default { Write-Host "Invalid option." -ForegroundColor Red }
    }

    Wait-Jarvis
}