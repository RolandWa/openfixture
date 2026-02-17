# Force Update OpenFixture Plugin
Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  OpenFixture - Force Update & Clean Cache ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan

# 1. Kill any running KiCAD processes
Write-Host "`n[1] Stopping KiCAD processes..." -ForegroundColor Yellow
$kicadProcesses = Get-Process | Where-Object { $_.Name -match "kicad|pcbnew" }
if ($kicadProcesses) {
    Write-Host "    Found running KiCAD processes - terminating..." -ForegroundColor Yellow
    $kicadProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "    ✅ KiCAD processes terminated" -ForegroundColor Green
} else {
    Write-Host "    ✅ No KiCAD processes running" -ForegroundColor Green
}

# 2. Clear ALL Python cache in KiCAD directory
Write-Host "`n[2] Clearing Python cache..." -ForegroundColor Yellow
$kicadBase = "C:\Users\RWache\OneDrive - Rockwell Automation, Inc\Simulation tools\KiCad\9.0"
$cleared = 0

# Clear __pycache__ directories
$pycacheDirs = Get-ChildItem "$kicadBase" -Recurse -Directory -Filter "__pycache__" -Force -ErrorAction SilentlyContinue
foreach ($dir in $pycacheDirs) {
    Remove-Item $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $cleared++
}

# Clear .pyc files  
$pycFiles = Get-ChildItem "$kicadBase" -Recurse -Filter "*.pyc" -Force -ErrorAction SilentlyContinue
foreach ($file in $pycFiles) {
    Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
    $cleared++
}

Write-Host "    ✅ Cleared $cleared cache items" -ForegroundColor Green

# 3. Force copy updated file
Write-Host "`n[3] Deploying updated plugin..." -ForegroundColor Yellow
$source = ".\openfixture.py"
$dest = "$kicadBase\3rdparty\plugins\openfixture.py"

if (Test-Path $source) {
    Copy-Item $source $dest -Force
    $srcHash = (Get-FileHash $source).Hash
    $dstHash = (Get-FileHash $dest).Hash
    
    if ($srcHash -eq $dstHash) {
        Write-Host "    ✅ File deployed successfully" -ForegroundColor Green
        Write-Host "       Size: $((Get-Item $dest).Length) bytes" -ForegroundColor Gray
    } else {
        Write-Host "    ❌ Hash mismatch after copy!" -ForegroundColor Red
    }
} else {
    Write-Host "    ❌ Source file not found!" -ForegroundColor Red
}

# 4. Verify CheckBox code is present
Write-Host "`n[4] Verifying CheckBox code..." -ForegroundColor Yellow
$hasCheckBox = Select-String -Path $dest -Pattern "wx\.CheckBox.*Top Layer" -Quiet
$hasRadioButton = Select-String -Path $dest -Pattern "wx\.RadioButton" -Quiet

if ($hasCheckBox) {
    Write-Host "    ✅ CheckBox code found in deployed file" -ForegroundColor Green
    $line = Select-String -Path $dest -Pattern "wx\.CheckBox.*Top Layer" | Select-Object -First 1
    Write-Host "       Line $($line.LineNumber): $($line.Line.Trim())" -ForegroundColor Gray
} else {
    Write-Host "    ❌ CheckBox code NOT found!" -ForegroundColor Red
}

if ($hasRadioButton) {
    Write-Host "    ⚠️  OLD RadioButton code still present!" -ForegroundColor Red
} else {
    Write-Host "    ✅ No RadioButton code (clean)" -ForegroundColor Green
}

# 5. Final instructions
Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NEXT STEPS                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n1. Start KiCAD fresh" -ForegroundColor White
Write-Host "2. Open your PCB board" -ForegroundColor White
Write-Host "3. Run: Tools → External Plugins → OpenFixture Generator" -ForegroundColor White
Write-Host "`n4. You should now see CHECKBOXES (square ☐), not radio buttons (○)" -ForegroundColor Yellow
Write-Host "   ☐ Top Layer (F.Cu)" -ForegroundColor Gray
Write-Host "   ☐ Bottom Layer (B.Cu)" -ForegroundColor Gray
Write-Host "`n5. You can check BOTH boxes to test both sides simultaneously" -ForegroundColor Green
Write-Host "`n"
