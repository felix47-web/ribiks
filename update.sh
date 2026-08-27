#!/bin/bash

set -e

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
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
    cd "$RIBIKS_DIR" || { echo "[!] Cannot access $RIBIKS_DIR"; exit 1; }
    git pull origin main
    echo ""
    echo "[*] Checking Tor (required for anonymity)..."
    if ! command -v tor &>/dev/null; then
        echo "[i] Tor not found. Installing..."
        if command -v pkg &>/dev/null; then
            pkg install -y tor
        elif command -v apt &>/dev/null; then
            sudo apt install -y tor
        else
            echo "[!] Please install Tor manually: pkg install tor  (or: sudo apt install tor)"
            echo "[i] Anonymity will be unavailable until Tor is installed."
        fi
    fi
    echo ""
    echo "[*] Installing/updating dependencies..."
    if [ -d "$RIBIKS_DIR/venv" ]; then
        "$RIBIKS_DIR/venv/bin/pip" install telethon requests aiohttp python-socks 2>/dev/null || true
    fi
    echo "[+] Updated via git pull!"
    echo "[i] Version: $(python3 -c 'from ribiks import __version__; print(__version__)' 2>/dev/null || echo 'unknown')"

elif [ -f "$INSTALL_DIR/ribiks.pyz" ]; then
    echo "[i] Detected: .pyz installation"
    echo "[*] Downloading latest release..."
    mkdir -p "$INSTALL_DIR"
    curl -sL "https://github.com/felix47-web/ribiks/releases/latest/download/ribiks.pyz" -o "$INSTALL_DIR/ribiks.pyz"
    chmod +x "$INSTALL_DIR/ribiks.pyz"
    echo "[+] Updated .pyz to latest version!"

    echo "[*] Checking Tor (required for anonymity)..."
    if ! command -v tor &>/dev/null; then
        echo "[i] Tor not found. Installing..."
        if command -v pkg &>/dev/null; then
            pkg install -y tor
        elif command -v apt &>/dev/null; then
            sudo apt install -y tor
        else
            echo "[!] Please install Tor manually: pkg install tor  (or: sudo apt install tor)"
        fi
    fi

    echo "[*] Checking python-socks (Telethon proxy)..."
    if ! python3 -c "import python_socks" 2>/dev/null; then
        echo "[i] Installing python-socks..."
        python3 -m pip install python-socks 2>/dev/null || true
    fi

else
    echo "[!] No existing installation found at:"
    echo "    Git: $RIBIKS_DIR"
    echo "    PYZ: $INSTALL_DIR/ribiks.pyz"
    echo ""
    echo "[i] Install fresh with:"
    echo "    git clone https://github.com/felix47-web/ribiks.git ~/ribiks"
    echo "    cd ~/ribiks && chmod +x install.sh && ./install.sh"
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
