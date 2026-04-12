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

# Plugin directory name (matches build.py)
$PluginDirName = "com_github_RolandWa_openfixture"

# Full plugin directory path
$PluginInstallDir = Join-Path $PluginsDir $PluginDirName

# Support files subdirectory (inside plugin directory)
$SupportDir = Join-Path $PluginInstallDir "openfixture_support"

Write-Host "`n[*] Synchronizing OpenFixture Plugin to KiCad...`n" -ForegroundColor Cyan

# Verify plugin directory exists
if (-not (Test-Path $PluginsDir)) {
    Write-Host "[ERROR] KiCad plugins directory not found!" -ForegroundColor Red
    Write-Host "   Path: $PluginsDir" -ForegroundColor Yellow
    Write-Host "`nPlease verify the path is correct or create the directory.`n" -ForegroundColor Yellow
    exit 1
}

# Create plugin directory if it doesn't exist
if (-not (Test-Path $PluginInstallDir)) {
    New-Item -ItemType Directory -Path $PluginInstallDir -Force | Out-Null
    Write-Host "[*] Created plugin directory: $PluginDirName" -ForegroundColor Gray
}

# Create support directory if it doesn't exist
if (-not (Test-Path $SupportDir)) {
    New-Item -ItemType Directory -Path $SupportDir -Force | Out-Null
    Write-Host "[*] Created support directory: openfixture_support" -ForegroundColor Gray
}

# Source directory (new src-layout structure)
$SrcDir = Join-Path $RepoDir "src"
$BuildDir = Join-Path $RepoDir "build"
$BuildPluginDir = Join-Path $BuildDir $PluginDirName

# Plugin files to sync to plugin directory (com_github_RolandWa_openfixture/)
$PluginFiles = @(
    @{Src = "src\openfixture.py"; Dest = "openfixture.py"},
    @{Src = "OpenFixture.png"; Dest = "OpenFixture.png"},
    @{Src = "build\$PluginDirName\__init__.py"; Dest = "__init__.py"},
    @{Src = "build\$PluginDirName\plugin.json"; Dest = "plugin.json"},
    @{Src = "build\$PluginDirName\metadata.json"; Dest = "metadata.json"}
)

# Supporting files to sync to openfixture_support subdirectory
$SupportFiles = @(
    @{Src = "src\openfixture_support\GenFixture.py"; Dest = "GenFixture.py"},
    @{Src = "src\openfixture_support\openfixture.scad"; Dest = "openfixture.scad"},
    @{Src = "src\openfixture_support\fixture_config.toml"; Dest = "fixture_config.toml"},
    @{Src = "src\openfixture_support\__init__.py"; Dest = "__init__.py"},
    @{Src = "glaser-stencil-d.ttf"; Dest = "glaser-stencil-d.ttf"},
    @{Src = "osh_logo.dxf"; Dest = "osh_logo.dxf"},
    @{Src = "genfixture.bat"; Dest = "genfixture.bat"},
    @{Src = "genfixture.sh"; Dest = "genfixture.sh"}
)

# Documentation files to sync to plugin directory (same level as openfixture.py)
$DocumentationFiles = @(
    @{Src = "README.md"; Dest = "README.md"},
    @{Src = "LICENSE.md"; Dest = "LICENSE.md"},
    @{Src = "POGO_PINS.md"; Dest = "POGO_PINS.md"},
    @{Src = "MIGRATION_GUIDE.md"; Dest = "MIGRATION_GUIDE.md"},
    @{Src = "SECURITY.md"; Dest = "SECURITY.md"}
)

$PluginSynced = 0
$SupportSynced = 0
$DocsSynced = 0
$FailedCount = 0

# Sync plugin files to plugin directory (com_github_RolandWa_openfixture/)
Write-Host "[*] Plugin Files:" -ForegroundColor Cyan
foreach ($File in $PluginFiles) {
    $SourcePath = Join-Path $RepoDir $File.Src
    $DestFile = $File.Dest
    
    if (Test-Path $SourcePath) {
        try {
            Copy-Item $SourcePath -Destination (Join-Path $PluginInstallDir $DestFile) -Force
            $FileInfo = Get-Item (Join-Path $PluginInstallDir $DestFile)
            $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
            Write-Host "   [OK] $DestFile ($SizeKB" "KB)" -ForegroundColor Green
            $PluginSynced++
        }
        catch {
            Write-Host "   [FAIL] Failed to copy $DestFile" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Yellow
            $FailedCount++
        }
    }
    else {
        Write-Host "   [WARN] $($File.Src) not found in repository" -ForegroundColor Yellow
        $FailedCount++
    }
}

# Sync supporting files
Write-Host "`n[*] Supporting Files:" -ForegroundColor Cyan
foreach ($File in $SupportFiles) {
    $SourcePath = Join-Path $RepoDir $File.Src
    $DestFile = $File.Dest
    
    if (Test-Path $SourcePath) {
        try {
            Copy-Item $SourcePath -Destination (Join-Path $SupportDir $DestFile) -Force
            $FileInfo = Get-Item (Join-Path $SupportDir $DestFile)
            $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
            Write-Host "   [OK] $DestFile ($SizeKB" "KB)" -ForegroundColor Green
            $SupportSynced++
        }
        catch {
            Write-Host "   [FAIL] Failed to copy $DestFile" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Yellow
            $FailedCount++
        }
    }
    else {
        Write-Host "   [WARN] $($File.Src) not found in repository" -ForegroundColor Yellow
        $FailedCount++
    }
}

# Sync documentation files to plugin directory (same level as openfixture.py)
Write-Host "`n[*] Documentation Files:" -ForegroundColor Cyan
foreach ($File in $DocumentationFiles) {
    $SourcePath = Join-Path $RepoDir $File.Src
    $DestFile = $File.Dest
    
    if (Test-Path $SourcePath) {
        try {
            Copy-Item $SourcePath -Destination (Join-Path $PluginInstallDir $DestFile) -Force
            $FileInfo = Get-Item (Join-Path $PluginInstallDir $DestFile)
            $SizeKB = [math]::Round($FileInfo.Length / 1KB, 2)
            Write-Host "   [OK] $DestFile ($SizeKB" "KB)" -ForegroundColor Green
            $DocsSynced++
        }
        catch {
            Write-Host "   [FAIL] Failed to copy $DestFile" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Yellow
            $FailedCount++
        }
    }
    else {
        Write-Host "   ⚠️  $($File.Src) not found in repository" -ForegroundColor Yellow
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
Get-ChildItem -Path $PluginInstallDir -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $CacheCleared++
}

# Remove .pyc files
Get-ChildItem -Path $PluginInstallDir -Filter "*.pyc" -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    $CacheCleared++
}

if ($CacheCleared -gt 0) {
    Write-Host "   [OK] Cleared $CacheCleared cache item(s)" -ForegroundColor Gray
} else {
    Write-Host "   [OK] No cache to clear" -ForegroundColor Gray
}

Write-Host "`n[*] File Locations:" -ForegroundColor Cyan
Write-Host "   Plugin Directory: $PluginInstallDir" -ForegroundColor Gray
Write-Host "   Support Directory: $SupportDir" -ForegroundColor Gray

Write-Host "`nTips:" -ForegroundColor Yellow
Write-Host "   - Restart KiCad to reload the updated plugin" -ForegroundColor Gray
Write-Host "   - OpenFixture is fully compatible with KiCad 8.0 and 9.0+" -ForegroundColor Gray
Write-Host "   - Structure matches build.py: $PluginDirName\" -ForegroundColor Gray
Write-Host ""
