#!/usr/bin/env bash
# ==============================================================================
# Build CODER-OS ISO inside Arch Linux Docker Container
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Building CODER-OS using official Arch Linux Docker container..."

docker run --privileged --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    archlinux:latest \
    bash -c "pacman -Syu --noconfirm archiso && bash ./scripts/build-iso.sh"

echo "ISO Build finished!"
