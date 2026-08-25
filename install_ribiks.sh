#!/bin/bash

set -e

INSTALL_DIR="$HOME/.ribiks"
BIN_DIR="$PREFIX/bin"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       Installing Ribiks...           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[!] Python3 not found."
    echo "[i] Install with: pkg install python"
    exit 1
fi

# Create install directory
mkdir -p "$INSTALL_DIR"

# Download the pyz
echo "[*] Downloading Ribiks..."
curl -sL "https://github.com/felix47-web/ribiks/releases/latest/download/ribiks.pyz" -o "$INSTALL_DIR/ribiks.pyz"

if [ ! -f "$INSTALL_DIR/ribiks.pyz" ]; then
    echo "[!] Download failed. Check your internet connection."
    exit 1
fi

chmod +x "$INSTALL_DIR/ribiks.pyz"

# Create launcher
cat > "$BIN_DIR/ribiks" << LAUNCHER
#!/bin/bash
exec python3 "$INSTALL_DIR/ribiks.pyz" "\$@"
LAUNCHER
chmod +x "$BIN_DIR/ribiks"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║    Installation Complete!            ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Run: ribiks"
echo "  First time: ribiks setup"
echo ""
