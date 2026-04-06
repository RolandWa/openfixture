#!/bin/bash
#
# OpenFixture Generator - Modernized Wrapper Script
# Uses GenFixture.py with TOML configuration support
#
# Original: Elliot Buller - Tiny Labs Inc (2016)
# Modernization Contributors (2026)
# License: CC-BY-SA 4.0
#
# Usage: ./genfixture.sh <path_to_board.kicad_pcb>
#

# Get board file from command line
BOARD=$1

if [ -z "$BOARD" ]; then
    echo "Error: No board file specified"
    echo "Usage: ./genfixture.sh <path_to_board.kicad_pcb>"
    exit 1
fi

if [ ! -f "$BOARD" ]; then
    echo "Error: Board file not found: $BOARD"
    exit 1
fi

# ============================================================================
# PROJECT-SPECIFIC PARAMETERS
# Edit these values for your project, or use fixture_config.toml instead
# ============================================================================

# Board parameters
PCB_TH=1.6
LAYER='F.Cu'
REV='rev_01'

# Material parameters
MAT_TH=3.0

# Hardware parameters (M3 standard)
SCREW_LEN=16.0
SCREW_D=3.0
NUT_TH=2.4
NUT_F2F=5.45
NUT_C2C=6.10
WASHER_TH=1.0

# Advanced parameters
BORDER=0.8
POGO_LENGTH=16.0

# Output directory
OUTPUT="fixture-${REV}"

# ============================================================================
# Check for TOML configuration file
# ============================================================================

CONFIG_FILE="fixture_config.toml"

if [ -f "$CONFIG_FILE" ]; then
    echo "Found configuration file: $CONFIG_FILE"
    echo "Configuration will override default parameters"
    USE_CONFIG="--config $CONFIG_FILE"
else
    echo "No configuration file found, using script parameters"
    USE_CONFIG=""
fi

# ============================================================================
# Run GenFixture_v2.py
# ============================================================================

echo ""
echo "OpenFixture Generator"
echo "======================"
echo "Board: $BOARD"
echo "Output: $OUTPUT"
echo ""

python3 GenFixture.py \
    --board "$BOARD" \
    --mat_th $MAT_TH \
    --out "$OUTPUT" \
    --pcb_th $PCB_TH \
    --layer $LAYER \
    --rev $REV \
    --screw_len $SCREW_LEN \
    --screw_d $SCREW_D \
    --nut_th $NUT_TH \
    --nut_f2f $NUT_F2F \
    --nut_c2c $NUT_C2C \
    --washer_th $WASHER_TH \
    --border $BORDER \
    --pogo-uncompressed-length $POGO_LENGTH \
    $USE_CONFIG \
    --verbose

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "SUCCESS! Fixture generated in $OUTPUT"
    echo "========================================"
    echo ""
    echo "Files generated:"
    echo "  - $OUTPUT/*-fixture.dxf  (laser-cut file)"
    echo "  - $OUTPUT/*-fixture.png  (3D preview)"
    echo "  - $OUTPUT/*-test.dxf     (test cut)"
    echo "  - $OUTPUT/*-outline.dxf  (board outline)"
    echo "  - $OUTPUT/*-track.dxf    (verification)"
    echo ""
    
    # Open output directory (platform-specific)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "$OUTPUT"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open "$OUTPUT" 2>/dev/null || echo "Open $OUTPUT to view results"
    fi
else
    echo ""
    echo "========================================"
    echo "ERROR: Fixture generation failed"
    echo "========================================"
    echo "Please check the error messages above"
    exit 1
fi
