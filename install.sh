#!/bin/bash

set -e

RIBIKS_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$RIBIKS_DIR/venv"
BIN_DIR="$PREFIX/bin"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       Installing Ribiks...           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

echo "[*] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "[!] Python3 not found. Install with: pkg install python"
    exit 1
fi

echo "[*] Creating virtual environment..."
python3 -m venv "$VENV_DIR" || {
    echo "[!] venv failed, trying without pip..."
    python3 -m venv "$VENV_DIR" --without-pip
}

echo "[*] Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip 2>/dev/null || true
"$VENV_DIR/bin/pip" install telethon requests

echo "[*] Setting up ribiks launcher..."
cat > "$BIN_DIR/ribiks" << LAUNCHER
#!/bin/bash
export PYTHONPATH="$RIBIKS_DIR:\$PYTHONPATH"
exec "$VENV_DIR/bin/python" -m ribiks.cli "\$@"
LAUNCHER
chmod +x "$BIN_DIR/ribiks"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║    Installation Complete!            ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Run 'ribiks' to start"
echo "  Run 'ribiks setup' for first-time configuration"
echo ""
