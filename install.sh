#!/bin/bash
# AeroCore installer
# Usage:
#   curl -sSL https://raw.githubusercontent.com/Guajardian/AeroCore/main/install.sh | bash

set -e

REPO_URL="https://github.com/Guajardian/AeroCore.git"
INSTALL_DIR="$HOME/AeroCore"
SERVICE_NAME="aerocore"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AeroCore Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Check for git ──
if ! command -v git &>/dev/null; then
    echo "▸ Installing git..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq git
fi

# ── Check for python3-venv ──
if ! python3 -m venv --help &>/dev/null 2>&1; then
    echo "▸ Installing python3-venv..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-venv
fi

# ── Clone or update repo ──
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "▸ AeroCore already installed at $INSTALL_DIR"
    echo "  Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "▸ Cloning AeroCore..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ── Create virtual environment ──
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "▸ Creating virtual environment..."
    python3 -m venv venv
fi

# ── Install dependencies ──
echo "▸ Installing dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -r requirements.txt --quiet

# ── Check I2C ──
echo ""
if [ -e /dev/i2c-1 ]; then
    echo "✓ I2C is enabled"
else
    echo "⚠ I2C does not appear to be enabled."
    echo "  Run: sudo raspi-config → Interface Options → I2C → Enable"
    echo "  Then reboot and run this installer again."
fi

# ── Set up systemd service ──
echo ""
read -rp "▸ Set up AeroCore to start on boot? [Y/n] " AUTOSTART
AUTOSTART=${AUTOSTART:-Y}

if [[ "$AUTOSTART" =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=AeroCore Fan Controller
After=network.target

[Service]
ExecStart=${INSTALL_DIR}/venv/bin/python3 ${INSTALL_DIR}/app.py
WorkingDirectory=${INSTALL_DIR}
User=$(whoami)
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    echo "✓ Systemd service created and enabled"

    read -rp "▸ Start AeroCore now? [Y/n] " START_NOW
    START_NOW=${START_NOW:-Y}
    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        sudo systemctl start "$SERVICE_NAME"
        echo ""
        IP=$(hostname -I | awk '{print $1}')
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  AeroCore is running!"
        echo "  Open http://${IP}:5000"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
else
    echo ""
    echo "✓ Installation complete. To start manually:"
    echo "    cd $INSTALL_DIR"
    echo "    source venv/bin/activate"
    echo "    python app.py"
fi

echo ""
echo "✓ Done."
