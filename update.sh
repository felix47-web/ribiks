#!/bin/bash

set -e

RIBIKS_DIR="$HOME/ribiks"
INSTALL_DIR="$HOME/.ribiks"
BIN_DIR="$PREFIX/bin"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       Updating Ribiks...             ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Detect installation type and update
if [ -d "$RIBIKS_DIR/.git" ]; then
    echo "[i] Detected: git installation"
    echo "[*] Pulling latest changes..."
    cd "$RIBIKS_DIR"
    git pull origin main
    echo ""
    echo "[+] Updated via git pull!"
    echo "[i] Version: $(python3 -c 'from ribiks import __version__; print(__version__)' 2>/dev/null || echo 'unknown')"

elif [ -f "$INSTALL_DIR/ribiks.pyz" ]; then
    echo "[i] Detected: .pyz installation"
    echo "[*] Downloading latest release..."
    curl -sL "https://github.com/felix47-web/ribiks/releases/latest/download/ribiks.pyz" -o "$INSTALL_DIR/ribiks.pyz"
    chmod +x "$INSTALL_DIR/ribiks.pyz"
    echo "[+] Updated .pyz to latest version!"

else
    echo "[!] No existing installation found."
    echo "[i] Install fresh with:"
    echo "    curl -fsSL https://raw.githubusercontent.com/felix47-web/ribiks/main/update.sh | bash"
    exit 1
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║    Update Complete!                  ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Run 'ribiks' to start"
echo "  Run 'ribiks update' for future updates"
echo ""
