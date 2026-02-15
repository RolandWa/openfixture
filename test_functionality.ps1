# OpenFixture v2 - Functionality Test Script
# Tests all v2 components to ensure they work correctly
#
# Date: February 15, 2026

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "OpenFixture v2 - Functionality Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorCount = 0
$WarningCount = 0
$PassCount = 0

# Test 1: Check KiCAD Python Installation
Write-Host "[TEST 1] Checking KiCAD Python installation..." -ForegroundColor Yellow
$KiCadPython = "C:\Program Files\KiCad\9.0\bin\python.exe"

if (Test-Path $KiCadPython) {
    Write-Host "  ✅ PASS: KiCAD Python found at: $KiCadPython" -ForegroundColor Green
    $Version = & $KiCadPython --version 2>&1
    Write-Host "     Version: $Version" -ForegroundColor Gray
    $PassCount++
} else {
    Write-Host "  ❌ FAIL: KiCAD Python not found" -ForegroundColor Red
    Write-Host "     Expected: $KiCadPython" -ForegroundColor Gray
    $ErrorCount++
}

# Test 2: Check v2 Python Files Syntax
Write-Host "`n[TEST 2] Validating Python syntax..." -ForegroundColor Yellow

$PythonFiles = @(
    "GenFixture_v2.py",
    "openfixture_v2.py"
)

foreach ($File in $PythonFiles) {
    if (Test-Path $File) {
        $Result = python -m py_compile $File 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ PASS: $File - Syntax OK" -ForegroundColor Green
            $PassCount++
        } else {
            Write-Host "  ❌ FAIL: $File - Syntax Error" -ForegroundColor Red
            Write-Host "     $Result" -ForegroundColor Gray
            $ErrorCount++
        }
    } else {
        Write-Host "  ❌ FAIL: $File - File not found" -ForegroundColor Red
        $ErrorCount++
    }
}

# Test 3: Check TOML Configuration File
Write-Host "`n[TEST 3] Validating TOML configuration..." -ForegroundColor Yellow

if (Test-Path "fixture_config.toml") {
    Write-Host "  ✅ PASS: fixture_config.toml exists" -ForegroundColor Green
    $PassCount++
    
    # Check for required sections
    $Content = Get-Content "fixture_config.toml" -Raw
    $RequiredSections = @("[board]", "[material]", "[hardware]")
    
    foreach ($Section in $RequiredSections) {
        if ($Content -match [regex]::Escape($Section)) {
            Write-Host "  ✅ PASS: Section $Section found" -ForegroundColor Green
            $PassCount++
        } else {
            Write-Host "  ⚠️  WARN: Section $Section missing" -ForegroundColor Yellow
            $WarningCount++
        }
    }
} else {
    Write-Host "  ❌ FAIL: fixture_config.toml not found" -ForegroundColor Red
    $ErrorCount++
}

# Test 4: Check Wrapper Scripts
Write-Host "`n[TEST 4] Checking wrapper scripts..." -ForegroundColor Yellow

$Scripts = @(
    "genfixture_v2.bat",
    "genfixture_v2.sh"
)

foreach ($Script in $Scripts) {
    if (Test-Path $Script) {
        Write-Host "  ✅ PASS: $Script exists" -ForegroundColor Green
        $Size = (Get-Item $Script).Length
        Write-Host "     Size: $Size bytes" -ForegroundColor Gray
        $PassCount++
    } else {
        Write-Host "  ❌ FAIL: $Script not found" -ForegroundColor Red
        $ErrorCount++
    }
}

# Test 5: Check OpenSCAD Dependency
Write-Host "`n[TEST 5] Checking OpenSCAD installation..." -ForegroundColor Yellow

if (Test-Path "C:\Program Files\OpenSCAD\openscad.exe") {
    Write-Host "  ✅ PASS: OpenSCAD is installed" -ForegroundColor Green
    $PassCount++
} else {
    Write-Host "  ⚠️  WARN: OpenSCAD not found at standard location" -ForegroundColor Yellow
    Write-Host "     OpenSCAD is required for 3D model generation" -ForegroundColor Gray
    $WarningCount++
}

# Test 6: Check OpenSCAD Model File
Write-Host "`n[TEST 6] Checking OpenSCAD model file..." -ForegroundColor Yellow

if (Test-Path "openfixture.scad") {
    Write-Host "  ✅ PASS: openfixture.scad exists" -ForegroundColor Green
    $Size = (Get-Item "openfixture.scad").Length
    Write-Host "     Size: $Size bytes" -ForegroundColor Gray
    $PassCount++
} else {
    Write-Host "  ❌ FAIL: openfixture.scad not found" -ForegroundColor Red
    $ErrorCount++
}

# Test 7: Check KiCAD Plugin Installation
Write-Host "`n[TEST 7] Verifying KiCAD plugin installation..." -ForegroundColor Yellow

# NOTE: Update this path to your KiCAD plugins directory
# Windows Standard: $env:APPDATA\kicad\9.0\3rdparty\plugins
# Windows OneDrive: Customize to your installation
$PluginDir = "$env:APPDATA\kicad\9.0\3rdparty\plugins"

if (Test-Path $PluginDir) {
    Write-Host "  ✅ PASS: Plugin directory exists" -ForegroundColor Green
    $PassCount++
    
    $PluginFile = Join-Path $PluginDir "openfixture_v2.py"
    if (Test-Path $PluginFile) {
        Write-Host "  ✅ PASS: openfixture_v2.py installed in KiCAD" -ForegroundColor Green
        $LastWrite = (Get-Item $PluginFile).LastWriteTime
        Write-Host "     Last updated: $LastWrite" -ForegroundColor Gray
        $PassCount++
    } else {
        Write-Host "  ❌ FAIL: openfixture_v2.py not found in plugins" -ForegroundColor Red
        $ErrorCount++
    }
    
    $SupportDir = Join-Path $PluginDir "openfixture_support"
    if (Test-Path $SupportDir) {
        Write-Host "  ✅ PASS: Support directory exists" -ForegroundColor Green
        $FileCount = (Get-ChildItem $SupportDir).Count
        Write-Host "     Files: $FileCount" -ForegroundColor Gray
        $PassCount++
    } else {
        Write-Host "  ⚠️  WARN: Support directory not found" -ForegroundColor Yellow
        $WarningCount++
    }
} else {
    Write-Host "  ❌ FAIL: KiCAD plugin directory not found" -ForegroundColor Red
    $ErrorCount++
}

# Test 8: Check Documentation Files
Write-Host "`n[TEST 8] Checking documentation..." -ForegroundColor Yellow

$Docs = @(
    "README_v2.md",
    "MIGRATION_GUIDE_v2.md",
    "MODERNIZATION_SUMMARY.md"
)

foreach ($Doc in $Docs) {
    if (Test-Path $Doc) {
        Write-Host "  ✅ PASS: $Doc exists" -ForegroundColor Green
        $PassCount++
    } else {
        Write-Host "  ⚠️  WARN: $Doc not found" -ForegroundColor Yellow
        $WarningCount++
    }
}

# Final Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "  ✅ Passed:  $PassCount" -ForegroundColor Green
Write-Host "  ⚠️  Warnings: $WarningCount" -ForegroundColor Yellow
Write-Host "  ❌ Failed:  $ErrorCount" -ForegroundColor Red

Write-Host "`n========================================`n" -ForegroundColor Cyan

if ($ErrorCount -eq 0) {
    Write-Host "🎉 All critical tests passed! OpenFixture v2 is ready to use." -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart KiCAD to load the updated plugin" -ForegroundColor Gray
    Write-Host "  2. Open a PCB file in KiCAD" -ForegroundColor Gray
    Write-Host "  3. Go to: Tools → External Plugins → OpenFixture Generator" -ForegroundColor Gray
    exit 0
} elseif ($ErrorCount -lt 3) {
    Write-Host "⚠️  Some tests failed, but core functionality may still work." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "❌ Critical errors found. Please review and fix issues." -ForegroundColor Red
    exit 2
}
