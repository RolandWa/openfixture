@echo off
REM OpenFixture Generator - Modernized Wrapper Script
REM Uses GenFixture.py with TOML configuration support
REM
REM Original: Elliot Buller - Tiny Labs Inc (2016)
REM Modernization Contributors (2026)
REM License: CC-BY-SA 4.0
REM
REM Usage: genfixture.bat <path_to_board.kicad_pcb>

setlocal

REM Add OpenSCAD to PATH
IF EXIST "C:\Program Files\OpenSCAD" SET PATH=%PATH%;"C:\Program Files\OpenSCAD\"

REM Get board file from command line
set BOARD=%1

if "%BOARD%"=="" (
    echo Error: No board file specified
    echo Usage: genfixture.bat ^<path_to_board.kicad_pcb^>
    exit /b 1
)

REM Check if board file exists
if not exist "%BOARD%" (
    echo Error: Board file not found: %BOARD%
    exit /b 1
)

REM ============================================================================
REM PROJECT-SPECIFIC PARAMETERS
REM Edit these values for your project, or use fixture_config.toml instead
REM ============================================================================

REM Board parameters
set PCB_TH=1.6
set LAYER=F.Cu
set REV=rev_01

REM Material parameters
set MAT_TH=3.0

REM Hardware parameters (M3 standard)
set SCREW_LEN=16.0
set SCREW_D=3.0
set NUT_TH=2.4
set NUT_F2F=5.45
set NUT_C2C=6.10
set WASHER_TH=1.0

REM Advanced parameters
set BORDER=0.8
set POGO_LENGTH=16.0

REM Output directory
set OUTPUT=fixture-%REV%

REM ============================================================================
REM Check for TOML configuration file
REM ============================================================================

set CONFIG_FILE=fixture_config.toml

if exist "%CONFIG_FILE%" (
    echo Found configuration file: %CONFIG_FILE%
    echo Configuration will override default parameters
    set USE_CONFIG=--config %CONFIG_FILE%
) else (
    echo No configuration file found, using script parameters
    set USE_CONFIG=
)

REM ============================================================================
REM Run GenFixture_v2.py
REM ============================================================================

echo.
echo OpenFixture Generator
echo ======================
echo Board: %BOARD%
echo Output: %OUTPUT%
echo.

"C:\Program Files\KiCad\9.0\bin\python.exe" GenFixture.py ^
    --board "%BOARD%" ^
    --mat_th %MAT_TH% ^
    --out "%OUTPUT%" ^
    --pcb_th %PCB_TH% ^
    --layer %LAYER% ^
    --rev %REV% ^
    --screw_len %SCREW_LEN% ^
    --screw_d %SCREW_D% ^
    --nut_th %NUT_TH% ^
    --nut_f2f %NUT_F2F% ^
    --nut_c2c %NUT_C2C% ^
    --washer_th %WASHER_TH% ^
    --border %BORDER% ^
    --pogo-uncompressed-length %POGO_LENGTH% ^
    %USE_CONFIG% ^
    --verbose

REM Check result
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Fixture generated in %OUTPUT%
    echo ========================================
    echo.
    echo Files generated:
    echo   - %OUTPUT%\*-fixture.dxf  (laser-cut file)
    echo   - %OUTPUT%\*-fixture.png  (3D preview)
    echo   - %OUTPUT%\*-test.dxf     (test cut)
    echo   - %OUTPUT%\*-outline.dxf  (board outline)
    echo   - %OUTPUT%\*-track.dxf    (verification)
    echo.
    
    REM Open output directory
    explorer "%OUTPUT%"
) else (
    echo.
    echo ========================================
    echo ERROR: Fixture generation failed
    echo ========================================
    echo Please check the error messages above
    exit /b 1
)

endlocal
