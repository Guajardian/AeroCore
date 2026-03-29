#!/bin/bash
# AeroCore update script
# Usage:
#   From the AeroCore directory:  ./update.sh
#   Remote one-liner:             curl -sSL https://raw.githubusercontent.com/Guajardian/AeroCore/main/update.sh | bash

set -e

REPO_URL="https://github.com/Guajardian/AeroCore.git"
SERVICE_NAME="aerocore"

# ── Determine install directory ──
if [ -f "app.py" ] && grep -q "AeroCore\|aerocore" app.py 2>/dev/null; then
    INSTALL_DIR="$(pwd)"
elif [ -d "$HOME/AeroCore" ]; then
    INSTALL_DIR="$HOME/AeroCore"
elif [ -d "/home/pi/AeroCore" ]; then
    INSTALL_DIR="/home/pi/AeroCore"
else
    echo "AeroCore directory not found. Cloning fresh..."
    INSTALL_DIR="$HOME/AeroCore"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  AeroCore Updater"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Directory: $INSTALL_DIR"

# ── Pull latest changes ──
echo ""
echo "▸ Pulling latest changes..."
BEFORE=$(git rev-parse HEAD)
git pull origin main
AFTER=$(git rev-parse HEAD)

if [ "$BEFORE" = "$AFTER" ]; then
    echo "  Already up to date."
else
    echo "  Updated: $(git log --oneline "$BEFORE".."$AFTER" | wc -l) new commit(s)"
    git log --oneline "$BEFORE".."$AFTER" | sed 's/^/    /'
fi

# ── Update dependencies ──
echo ""
echo "▸ Updating dependencies..."
if [ -d "$INSTALL_DIR/venv" ]; then
    "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt --quiet
else
    pip install -r requirements.txt --quiet 2>/dev/null || pip3 install -r requirements.txt --quiet
fi

# ── Restart service if running ──
echo ""
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "▸ Restarting $SERVICE_NAME service..."
    sudo systemctl restart "$SERVICE_NAME"
    echo "  Service restarted."
else
    echo "▸ No systemd service detected. Restart AeroCore manually:"
    echo "    source venv/bin/activate && python app.py"
fi

echo ""
echo "✓ Update complete."
