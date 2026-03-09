#!/bin/bash
set -euo pipefail

# RF Site Telemetry Cloud API Installation Script
# Usage: sudo ./install.sh

if [[ $EUID -eq 0 ]]; then
    echo "This script should not be run as root. Run as a regular user with sudo access."
    exit 1
fi

# Configuration
INSTALL_DIR="/opt/rfsite"
VENV_DIR="$INSTALL_DIR/.venv"
CONFIG_DIR="/etc/rfsite-cloud-api"
LOG_DIR="/var/log/rfsite"
SERVICE_USER="www-data"

echo "Installing RF Site Telemetry Cloud API..."

# Create directories
echo "Creating directories..."
sudo mkdir -p "$INSTALL_DIR"
sudo mkdir -p "$CONFIG_DIR"
sudo mkdir -p "$LOG_DIR"

# Copy source code
echo "Copying source code..."
sudo cp -r cloud-api/* "$INSTALL_DIR/"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"

# Install dependencies
echo "Installing Python dependencies..."
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -e "$INSTALL_DIR"

# Copy configuration
echo "Setting up configuration..."
if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
    sudo cp "$INSTALL_DIR/config.example.yaml" "$CONFIG_DIR/config.yaml"
    echo "Configuration file created at $CONFIG_DIR/config.yaml"
    echo "Please edit it before starting the service."
else
    echo "Configuration file already exists at $CONFIG_DIR/config.yaml"
fi

# Set permissions
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
sudo chmod 755 "$CONFIG_DIR"
sudo chmod 644 "$CONFIG_DIR/config.yaml"

# Install systemd service
echo "Installing systemd service..."
sudo cp infra/deploy/systemd/rfsite-cloud-api.service /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit configuration: sudo nano $CONFIG_DIR/config.yaml"
echo "2. Enable service: sudo systemctl enable rfsite-cloud-api"
echo "3. Start service: sudo systemctl start rfsite-cloud-api"
echo "4. Check status: sudo systemctl status rfsite-cloud-api"
echo "5. View logs: sudo journalctl -u rfsite-cloud-api -f"
echo ""
echo "The API will be available at the configured host:port (default: 127.0.0.1:8001)"
