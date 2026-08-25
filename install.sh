#!/bin/bash

set -e

RIBIKS_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$RIBIKS_DIR/venv"
BIN_DIR="$HOME/.local/bin"

echo "╔══════════════════════════════════════╗"
echo "║       Installing Ribiks...           ║"
echo "╚══════════════════════════════════════╝"

echo "[*] Creating virtual environment..."
python3 -m venv "$VENV_DIR" 2>/dev/null || python3 -m venv "$VENV_DIR" --without-pip

echo "[*] Installing dependencies..."
"$VENV_DIR/bin/pip" install -q --upgrade pip 2>/dev/null || true
"$VENV_DIR/bin/pip" install -q telethon openai

echo "[*] Installing ribiks package..."
"$VENV_DIR/bin/pip" install -q -e "$RIBIKS_DIR"

echo "[*] Creating ribiks command..."
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/ribiks" << LAUNCHER
#!/bin/bash
exec "$VENV_DIR/bin/python" -m ribiks.cli "\$@"
LAUNCHER
chmod +x "$BIN_DIR/ribiks"

if ! echo "$PATH" | grep -q "$BIN_DIR"; then
    echo "[*] Adding $BIN_DIR to PATH..."
    SHELL_RC="$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
    export PATH="$BIN_DIR:$PATH"
fi

echo ""
echo "[+] Installation complete!"
echo "[i] Run 'ribiks' to start"
echo "[i] Run 'ribiks setup' for first-time configuration"
