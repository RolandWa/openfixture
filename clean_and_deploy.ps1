# OpenFixture - Clean and Force Deploy
# Completely clears cache and forces fresh deployment

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "OpenFixture - Clean Deploy" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Kill KiCAD
Write-Host "[1] Stopping KiCAD..." -ForegroundColor Yellow
$kicad = Get-Process | Where-Object { $_.Name -match "kicad|pcbnew" }
if ($kicad) {
    $kicad | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "    [OK] KiCAD stopped" -ForegroundColor Green
} else {
    Write-Host "    [OK] KiCAD not running" -ForegroundColor Green
}

# Step 2: Clear ALL Python cache
Write-Host "`n[2] Clearing Python cache..." -ForegroundColor Yellow
# User should set KICAD_PATH environment variable or modify this path
$kicadBase = $env:KICAD_PATH ?? "$env:APPDATA\KiCad\9.0"
$cleared = 0

Get-ChildItem "$kicadBase" -Recurse -Directory -Filter "__pycache__" -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $cleared++
}

Get-ChildItem "$kicadBase" -Recurse -Filter "*.pyc" -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    $cleared++
}

Write-Host "    [OK] Cleared $cleared cache items" -ForegroundColor Green

# Step 3: Deploy fresh files
Write-Host "`n[3] Deploying fresh files..." -ForegroundColor Yellow
.\sync_to_kicad.ps1 | Out-Null

# Step 4: Verify
Write-Host "`n[4] Verifying deployment..." -ForegroundColor Yellow

$pluginFile = "$kicadBase\3rdparty\plugins\openfixture.py"
$hasCheckBox = Select-String -Path $pluginFile -Pattern "wx\.CheckBox.*Top Layer" -Quiet

if ($hasCheckBox) {
    Write-Host "    [OK] CheckBox code verified" -ForegroundColor Green
} else {
    Write-Host "    [FAIL] CheckBox code NOT found!" -ForegroundColor Red
}

# Check GenFixture.py exists
$genFixture = "$kicadBase\3rdparty\plugins\openfixture_support\GenFixture.py"
if (Test-Path $genFixture) {
    Write-Host "    [OK] GenFixture.py exists" -ForegroundColor Green
} else {
    Write-Host "    [FAIL] GenFixture.py missing!" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Start KiCAD" -ForegroundColor White
Write-Host "2. Open your PCB" -ForegroundColor White
Write-Host "3. Tools -> External Plugins -> OpenFixture Generator" -ForegroundColor White
Write-Host "4. You should see CHECKBOXES (not radio buttons)" -ForegroundColor White
Write-Host "`n"
