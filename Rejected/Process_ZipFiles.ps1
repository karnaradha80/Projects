# ============================================================
# Process_ZipFiles.ps1
# Reads a file list, picks zips from Source, unzips them,
# adds .txt extension to extension-less files, and moves
# the .txt file directly to Target.
# ============================================================

# ---------- CONFIG ------------------------------------------
$RootDir       = "C:\Projects\Rejected"
$FileListPath  = "$RootDir\filelist.txt"
$SourceDir     = "$RootDir\1_Source"
$InProgressDir = "$RootDir\2_inprogress"
$CompletedDir  = "$RootDir\4_Processed_Source_Files"
$TargetDir     = "$RootDir\3_Target"
$TempWorkDir   = "$RootDir\2_inprogress\work"
$SuccessLog    = "$RootDir\success_log.txt"
$ErrorLog      = "$RootDir\error_log.txt"
# ------------------------------------------------------------

$runStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $SuccessLog -Value ""
Add-Content -Path $SuccessLog -Value "=== Run: $runStamp ==="
Add-Content -Path $ErrorLog   -Value ""
Add-Content -Path $ErrorLog   -Value "=== Run: $runStamp ==="

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

Write-Host "Found $($fileList.Count) file(s) to process."

foreach ($zipFileName in $fileList) {

    $zipFileName = $zipFileName.Trim()
    if (-not $zipFileName.ToLower().EndsWith(".zip")) { $zipFileName = $zipFileName + ".zip" }
    $sourceZip = Join-Path $SourceDir $zipFileName
    $baseName  = [System.IO.Path]::GetFileNameWithoutExtension($zipFileName)

    # 1. Validate the zip exists in Source
    if (-not (Test-Path $sourceZip)) {
        Write-Warning "[$zipFileName] Not found in Source -- skipping."
        $ts = Get-Date -Format "HH:mm:ss"
        Add-Content -Path $ErrorLog -Value "$ts | $zipFileName | Not found in Source -- skipped."
        continue
    }

    Write-Host "[$zipFileName] Processing..."

    # 2. Move zip to Inprogress
    $inProgressZip = Join-Path $InProgressDir $zipFileName
    Move-Item -Path $sourceZip -Destination $inProgressZip -Force
    Write-Host "  Moved to Inprogress."

    # 3. Extract to a clean temp subfolder
    $extractDir = Join-Path $TempWorkDir $baseName
    if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
    New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

    try {
        Expand-Archive -Path $inProgressZip -DestinationPath $extractDir -Force
        Write-Host "  Extracted."
    }
    catch {
        Write-Warning "  Failed to extract $zipFileName : $_"
        $ts = Get-Date -Format "HH:mm:ss"
        Add-Content -Path $ErrorLog -Value "$ts | $zipFileName | Failed to extract: $_"
        continue
    }

    # 4. Add .txt to every file that has NO extension
    $allFiles     = Get-ChildItem -Path $extractDir -Recurse -File
    $renamedCount = 0

    foreach ($file in $allFiles) {
        if ($file.Extension -eq "") {
            Rename-Item -Path $file.FullName -NewName ($file.FullName + ".txt")
            $renamedCount++
        }
    }
    Write-Host "  Renamed $renamedCount extension-less file(s) to .txt."

    # 5. Move each .txt file directly to Target
    $allFiles  = Get-ChildItem -Path $extractDir -Recurse -File
    $moveFailed = $false

    foreach ($file in $allFiles) {
        $destPath = Join-Path $TargetDir $file.Name
        try {
            Move-Item -Path $file.FullName -Destination $destPath -Force
            Write-Host "  Moved $($file.Name) to Target."
        }
        catch {
            Write-Warning "  Failed to move $($file.Name) : $_"
            $ts = Get-Date -Format "HH:mm:ss"
            Add-Content -Path $ErrorLog -Value "$ts | $zipFileName | Failed to move $($file.Name): $_"
            $moveFailed = $true
        }
    }

    if ($moveFailed) { continue }

    # 6. Cleanup temp extract folder
    Remove-Item $extractDir -Recurse -Force

    # 7. Move original zip from Inprogress to Completed
    $completedZip = Join-Path $CompletedDir $zipFileName
    Move-Item -Path $inProgressZip -Destination $completedZip -Force
    Write-Host "  Original moved to Completed."

    $ts = Get-Date -Format "HH:mm:ss"
    Add-Content -Path $SuccessLog -Value "$ts | $zipFileName | Processed OK -- $renamedCount file(s) renamed, output: $baseName.txt"
    Write-Host "  [$zipFileName] Done."
}

# Cleanup empty work dir
if ((Get-ChildItem $TempWorkDir -Force | Measure-Object).Count -eq 0) {
    Remove-Item $TempWorkDir -Force
}

Write-Host "All files processed."
