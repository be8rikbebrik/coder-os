#!/usr/bin/env bash
# ==============================================================================
# CODER-OS ISO Build Script
# Usage: sudo ./scripts/build-iso.sh
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE_DIR="$PROJECT_ROOT/iso-profile"
WORK_DIR="/tmp/coderos-build-work"
OUT_DIR="$PROJECT_ROOT/out"

echo "=========================================================="
echo "   CODER-OS 1.0 • Automated ISO Builder                  "
echo "=========================================================="

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Error: This script must be run as root (sudo)."
    exit 1
fi

if ! command -v mkarchiso &> /dev/null; then
    echo "[!] Error: 'mkarchiso' not found. Installing 'archiso' package..."
    pacman -Sy --noconfirm archiso
fi

mkdir -p "$OUT_DIR"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

echo "[✓] Profile Directory: $PROFILE_DIR"
echo "[✓] Working Directory: $WORK_DIR"
echo "[✓] Output Directory:  $OUT_DIR"

# Ensure executable permissions on custom scripts inside airootfs
echo "[✓] Setting permissions on airootfs scripts..."
chmod +x "$PROFILE_DIR/airootfs/usr/bin/"* 2>/dev/null || true

echo "[*] Starting mkarchiso build process (this may take 5-15 minutes)..."
mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$PROFILE_DIR"

echo "=========================================================="
echo "   [✓] BUILD COMPLETE!                                  "
echo "   ISO file generated in: $OUT_DIR"
echo "=========================================================="
ls -lh "$OUT_DIR"/*.iso
