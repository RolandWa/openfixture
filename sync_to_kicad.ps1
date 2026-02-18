# OpenFixture Plugin - Sync to KiCad
# Automatically copies plugin files and supporting files from repository to KiCad
#
# Original: Elliot Buller - Tiny Labs Inc (2016)
# License: CC-BY-SA 4.0

$RepoDir = $PSScriptRoot

# Load configuration from external file (for security - keeps personal paths out of git)
$ConfigFile = Join-Path $RepoDir "sync_to_kicad_config.ps1"

if (Test-Path $ConfigFile) {
    # Load personal configuration
    . $ConfigFile
    Write-Host "[OK] Loaded configuration from: sync_to_kicad_config.ps1" -ForegroundColor Gray
} else {
    # Use default/fallback path (generic location)
    Write-Host "[WARN] Configuration file not found: sync_to_kicad_config.ps1" -ForegroundColor Yellow
    Write-Host "   Using default KiCad plugins directory..." -ForegroundColor Gray
    
    # Try to auto-detect KiCad plugins directory
    $DefaultPaths = @(
        "$env:APPDATA\kicad\9.0\3rdparty\plugins",
        "$env:APPDATA\kicad\8.0\3rdparty\plugins",
        "$HOME\.local\share\kicad\9.0\3rdparty\plugins",
        "$HOME\.local\share\kicad\8.0\3rdparty\plugins"
    )
    
    $PluginsDir = $null
    foreach ($Path in $DefaultPaths) {
        if (Test-Path $Path) {
            $PluginsDir = $Path
            Write-Host "   [OK] Auto-detected: $PluginsDir" -ForegroundColor Green
            break
        }
    }
    
    if (-not $PluginsDir) {
        Write-Host "`n[ERROR] Could not find KiCad plugins directory!" -ForegroundColor Red
        Write-Host "`n[*] To fix this:" -ForegroundColor Yellow
        Write-Host "   1. Copy sync_to_kicad_config.ps1.template to sync_to_kicad_config.ps1" -ForegroundColor Gray
        Write-Host "   2. Edit sync_to_kicad_config.ps1 with your KiCad plugins path" -ForegroundColor Gray
        Write-Host "   3. Run this script again" -ForegroundColor Gray
        Write-Host "`n   Example path: C:\Users\YourName\AppData\Roaming\kicad\9.0\3rdparty\plugins`n" -ForegroundColor Gray
        exit 1
    }
}

# OpenFixture support files directory (for scripts, SCAD, etc.)
$SupportDir = Join-Path $PluginsDir "openfixture_support"

Write-Host "`n[*] Synchronizing OpenFixture Plugin to KiCad...`n" -ForegroundColor Cyan

# Verify plugin directory exists
if (-not (Test-Path $PluginsDir)) {
    Write-Host "[ERROR] KiCad plugins directory not found!" -ForegroundColor Red
    Write-Host "   Path: $PluginsDir" -ForegroundColor Yellow
    Write-Host "`nPlease verify the path is correct or create the directory.`n" -ForegroundColor Yellow
    exit 1
}

# Create support directory if it doesn't exist
if (-not (Test-Path $SupportDir)) {
    New-Item -ItemType Directory -Path $SupportDir -Force | Out-Null
    Write-Host "[*] Created support directory: openfixture_support" -ForegroundColor Gray
}

# Plugin files to sync to KiCad plugins directory (flat structure)
$PluginFiles = @(
    "openfixture.py",
    "OpenFixtureDlg.py",
    "OpenFixture.png"
)

# Supporting files to sync to support subdirectory
$SupportFiles = @(
    "GenFixture.py",
    "openfixture.scad",
    "glaser-stencil-d.ttf",
    "osh_logo.dxf",
    "fixture_config.toml",
    "genfixture.bat",
    "genfixture.sh"
)

# Documentation files to sync to support subdirectory
$DocumentationFiles = @(
    "README.md",
    "POGO_PINS.md",
    "MIGRATION_GUIDE.md",
    "MODERNIZATION_SUMMARY.md",
    "SECURITY.md",
    "copilot-instructions_openfixture.md"
)

$PluginSynced = 0
$SupportSynced = 0
$DocsSynced = 0
$FailedCount = 0

# Sync plugin files to main plugins directory
Write-Host "[*] Plugin Files:" -ForegroundColor Cyan
foreach ($File in $PluginFiles) {
    $SourcePath = Join-Path $RepoDir $File
    
    if (Test-Path $SourcePath) {
        try {
            Copy-Item $SourcePath -Destination $PluginsDir -Force
            $FileInfo = Get-Item (Join-Path $PluginsDir $File)
            $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
            Write-Host "   [OK] $File ($SizeKB" "KB)" -ForegroundColor Green
            $PluginSynced++
        }
        catch {
            Write-Host "   [FAIL] Failed to copy $File" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Yellow
            $FailedCount++
        }
    }
    else {
        Write-Host "   [WARN] $File not found in repository" -ForegroundColor Yellow
        $FailedCount++
    }
}

# Sync supporting files
Write-Host "`n[*] Supporting Files:" -ForegroundColor Cyan
foreach ($File in $SupportFiles) {
    $SourcePath = Join-Path $RepoDir $File
    
    if (Test-Path $SourcePath) {
        try {
            Copy-Item $SourcePath -Destination $SupportDir -Force
            $FileInfo = Get-Item (Join-Path $SupportDir $File)
            $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
            Write-Host "   [OK] $File ($SizeKB" "KB)" -ForegroundColor Green
            $SupportSynced++
        }
        catch {
            Write-Host "   [FAIL] Failed to copy $File" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Yellow
            $FailedCount++
        }
    }
    else {
        Write-Host "   [WARN] $File not found in repository" -ForegroundColor Yellow
        $FailedCount++
    }
}

# Sync documentation files
Write-Host "`n[*] Documentation Files:" -ForegroundColor Cyan
foreach ($File in $DocumentationFiles) {
    $SourcePath = Join-Path $RepoDir $File
    
    if (Test-Path $SourcePath) {
        try {
            Copy-Item $SourcePath -Destination $SupportDir -Force
            $FileInfo = Get-Item (Join-Path $SupportDir $File)
            $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
            Write-Host "   [OK] $File ($SizeKB" "KB)" -ForegroundColor Green
            $DocsSynced++
        }
        catch {
            Write-Host "   [FAIL] Failed to copy $File" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Yellow
            $FailedCount++
        }
    }
    else {
        Write-Host "   ⚠️  $File not found in repository" -ForegroundColor Yellow
        $FailedCount++
    }
}

Write-Host "`n[*] Sync Summary:" -ForegroundColor Cyan
Write-Host "   Plugin Files:   $PluginSynced" -ForegroundColor Green
Write-Host "   Support Files:  $SupportSynced" -ForegroundColor Green
Write-Host "   Documentation:  $DocsSynced" -ForegroundColor Green
$TotalSynced = $PluginSynced + $SupportSynced + $DocsSynced
Write-Host "   Total Synced:   $TotalSynced files" -ForegroundColor Cyan
if ($FailedCount -gt 0) {
    Write-Host "   Failed:         $FailedCount files" -ForegroundColor Red
}

# Clear Python bytecode cache to force reload
Write-Host "`n[*] Clearing Python cache..." -ForegroundColor Cyan
$CacheCleared = 0

# Remove __pycache__ directories
Get-ChildItem -Path $PluginsDir -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $CacheCleared++
}

# Remove .pyc files
Get-ChildItem -Path $PluginsDir -Filter "*.pyc" -File -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    $CacheCleared++
}

if ($CacheCleared -gt 0) {
    Write-Host "   [OK] Cleared $CacheCleared cache item(s)" -ForegroundColor Gray
} else {
    Write-Host "   [OK] No cache to clear" -ForegroundColor Gray
}

Write-Host "`n[*] File Locations:" -ForegroundColor Cyan
Write-Host "   Plugin Directory: $PluginsDir" -ForegroundColor Gray
Write-Host "   Support Directory: $SupportDir" -ForegroundColor Gray

Write-Host "`nTips:" -ForegroundColor Yellow
Write-Host "   - Restart KiCad to reload the updated plugin" -ForegroundColor Gray
Write-Host "   - OpenFixture is fully compatible with KiCad 8.0 and 9.0+" -ForegroundColor Gray
Write-Host "   - Supporting files (scripts, configs) are in openfixture_support\" -ForegroundColor Gray
Write-Host ""
