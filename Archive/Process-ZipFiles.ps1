# ============================================================
# Process-ZipFiles.ps1
# Reads a file list, picks zips from Source, unzips them,
# adds .txt extension to extension-less files, rezips, and
# moves the final zip to Target.
# ============================================================

# ---------- CONFIG ------------------------------------------
$ArchiveRoot  = "C:\Projects\Archive"
$FileListPath = "$ArchiveRoot\filelist.txt"   # notepad file — one zip filename per line
$SourceDir    = "$ArchiveRoot\1_Source"
$InProgressDir= "$ArchiveRoot\2_inprogress"
$CompletedDir = "$ArchiveRoot\4_Processed_Source_Files"
$TargetDir    = "$ArchiveRoot\3_Target"
$TempWorkDir  = "$ArchiveRoot\2_inprogress\work"
# ------------------------------------------------------------

# Ensure all required folders exist
foreach ($dir in @($InProgressDir, $CompletedDir, $TargetDir, $TempWorkDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Validate file list exists
if (-not (Test-Path $FileListPath)) {
    Write-Error "File list not found: $FileListPath"
    exit 1
}

# Read zip filenames from the list (skip blank lines and comments)
$fileList = Get-Content $FileListPath | Where-Object { $_.Trim() -ne "" -and -not $_.StartsWith("#") }

if ($fileList.Count -eq 0) {
    Write-Host "No files listed in $FileListPath. Nothing to process."
    exit 0
}

Write-Host "Found $($fileList.Count) file(s) to process.`n"

foreach ($zipFileName in $fileList) {

    $zipFileName = $zipFileName.Trim()
    $sourceZip   = Join-Path $SourceDir $zipFileName

    # ── 1. Validate the zip exists in Source ────────────────
    if (-not (Test-Path $sourceZip)) {
        Write-Warning "[$zipFileName] Not found in Source — skipping."
        continue
    }

    Write-Host "[$zipFileName] Processing..."

    # ── 2. Move zip → Inprogress ────────────────────────────
    $inProgressZip = Join-Path $InProgressDir $zipFileName
    Move-Item -Path $sourceZip -Destination $inProgressZip -Force
    Write-Host "  Moved to Inprogress."

    # ── 3. Extract to a clean temp subfolder ────────────────
    $extractDir = Join-Path $TempWorkDir ([System.IO.Path]::GetFileNameWithoutExtension($zipFileName))
    if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
    New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

    try {
        Expand-Archive -Path $inProgressZip -DestinationPath $extractDir -Force
        Write-Host "  Extracted."
    }
    catch {
        Write-Warning "  Failed to extract $zipFileName : $_"
        continue
    }

    # ── 4. Add .txt to every file that has NO extension ─────
    $allFiles = Get-ChildItem -Path $extractDir -Recurse -File
    $renamedCount = 0

    foreach ($file in $allFiles) {
        if ($file.Extension -eq "") {
            $newName = $file.FullName + ".txt"
            Rename-Item -Path $file.FullName -NewName $newName
            $renamedCount++
        }
    }
    Write-Host "  Renamed $renamedCount extension-less file(s) to .txt."

    # ── 5. Rezip the processed files ────────────────────────
    $processedZip = Join-Path $TargetDir $zipFileName
    if (Test-Path $processedZip) { Remove-Item $processedZip -Force }

    try {
        Compress-Archive -Path "$extractDir\*" -DestinationPath $processedZip -Force
        Write-Host "  Rezipped to Target."
    }
    catch {
        Write-Warning "  Failed to rezip $zipFileName : $_"
        continue
    }

    # ── 6. Cleanup temp extract folder ──────────────────────
    Remove-Item $extractDir -Recurse -Force

    # ── 7. Move original zip from Inprogress → Completed ────
    $completedZip = Join-Path $CompletedDir $zipFileName
    Move-Item -Path $inProgressZip -Destination $completedZip -Force
    Write-Host "  Original moved to Inprogress\Completed."
    Write-Host "  [$zipFileName] Done.`n"
}

# Cleanup empty work dir
if ((Get-ChildItem $TempWorkDir -Force | Measure-Object).Count -eq 0) {
    Remove-Item $TempWorkDir -Force
}

Write-Host "All files processed."
