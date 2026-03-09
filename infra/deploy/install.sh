#!/bin/bash
set -euo pipefail

# RF Site Telemetry Cloud API Installation Script
# Usage: ./install.sh

if [[ $EUID -eq 0 ]]; then
    echo "This script should not be run as root. Run as a regular user with sudo access."
    exit 1
fi

# Configuration
INSTALL_DIR="/opt/rfsite"
VENV_DIR="$INSTALL_DIR/.venv"
CONFIG_DIR="/etc/rfsite-cloud-api"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
LOG_DIR="/var/log/rfsite"
SERVICE_USER="www-data"

echo "Installing/Updating RF Site Telemetry Cloud API..."

# Function to load database DSN from config file
get_db_dsn_from_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        python3 -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
        print(config.get('db_dsn', ''))
except:
    pass
" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Function to check if database exists
check_database_exists() {
    local dsn="$1"
    if [[ -z "$dsn" ]]; then
        return 1
    fi
    
    # Parse DSN: postgresql://user:password@host:port/database
    # Extract components using more robust parsing
    local user=$(echo "$dsn" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
    local password=$(echo "$dsn" | sed -n 's|postgresql://[^:]*:\([^@]*\)@.*|\1|p')
    local host=$(echo "$dsn" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    local port=$(echo "$dsn" | sed -n 's|.*@[^:]*:\([^/]*\)/.*|\1|p')
    local db_name=$(echo "$dsn" | sed -n 's|.*/\([^?]*\).*|\1|p')
    
    # Fallback for host without port
    if [[ -z "$host" ]]; then
        host=$(echo "$dsn" | sed -n 's|.*@\([^/]*\)/.*|\1|p')
        port="5432"
    fi
    
    if [[ -n "$db_name" && -n "$host" && -n "$user" ]]; then
        # Set password if available
        if [[ -n "$password" ]]; then
            export PGPASSWORD="$password"
        fi
        
        # Use port if specified, otherwise default
        local port_arg=""
        if [[ -n "$port" ]]; then
            port_arg="-p $port"
        fi
        
        psql -h "$host" $port_arg -U "$user" -d "$db_name" -c "SELECT 1;" >/dev/null 2>&1
        local result=$?
        
        # Clean up password from environment
        unset PGPASSWORD
        
        return $result
    else
        return 1
    fi
}

# Create directories
echo "Creating directories..."
sudo mkdir -p "$INSTALL_DIR"
sudo mkdir -p "$CONFIG_DIR"
sudo mkdir -p "$LOG_DIR"

# Copy source code
echo "Copying source code..."
sudo cp -r cloud-api/* "$INSTALL_DIR/"
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Create or update virtual environment
if [[ -d "$VENV_DIR" ]]; then
    echo "Virtual environment already exists, updating..."
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -e "$INSTALL_DIR"
else
    echo "Creating Python virtual environment..."
    sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -e "$INSTALL_DIR"
fi

# Setup configuration
echo "Setting up configuration..."
if [[ ! -f "$CONFIG_FILE" ]]; then
    sudo cp "$INSTALL_DIR/config.example.yaml" "$CONFIG_FILE"
    echo "Configuration file created at $CONFIG_FILE"
    echo "Please edit it before starting the service."
    CONFIG_CREATED=true
else
    echo "Configuration file already exists at $CONFIG_FILE"
    CONFIG_CREATED=false
fi

# Set permissions
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
sudo chmod 755 "$CONFIG_DIR"
sudo chmod 644 "$CONFIG_FILE"

# Check database setup
echo "Checking database setup..."
DB_DSN=$(get_db_dsn_from_config)

if [[ -n "$DB_DSN" ]]; then
    if check_database_exists "$DB_DSN"; then
        echo "Database connection successful."
    else
        echo "Warning: Could not connect to database with configured DSN."
        echo "Please verify database configuration and ensure the database exists."
        echo "You may need to run the migrations manually:"
        echo "  psql -h <host> -U <user> -d <database> -f infra/migrations/0001_init.sql"
        echo "  psql -h <host> -U <user> -d <database> -f infra/migrations/0002_api_keys.sql"
    fi
else
    if [[ "$CONFIG_CREATED" == "true" ]]; then
        echo "Please configure the database connection in $CONFIG_FILE"
        echo "Then run the migrations:"
        echo "  psql -h <host> -U <user> -d <database> -f infra/migrations/0001_init.sql"
        echo "  psql -h <host> -U <user> -d <database> -f infra/migrations/0002_api_keys.sql"
    else
        echo "Warning: Could not read database configuration from $CONFIG_FILE"
    fi
fi

# Install systemd service
echo "Installing systemd service..."
sudo cp infra/deploy/systemd/rfsite-cloud-api.service /etc/systemd/system/
sudo systemctl daemon-reload

# Test configuration loading
echo "Testing configuration..."
if sudo -u "$SERVICE_USER" "$VENV_DIR/bin/python3" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR/src')
from app.settings import Settings
try:
    settings = Settings('$CONFIG_FILE')
    print('Configuration loaded successfully')
except Exception as e:
    print(f'Configuration error: {e}')
    sys.exit(1)
"; then
    echo "Configuration test passed."
else
    echo "Warning: Configuration test failed. Please check $CONFIG_FILE"
fi

echo ""
echo "Installation/Update complete!"
echo ""
if [[ "$CONFIG_CREATED" == "true" ]]; then
    echo "Next steps:"
    echo "1. Edit configuration: sudo nano $CONFIG_FILE"
    echo "2. Setup database and run migrations if needed"
    echo "3. Enable service: sudo systemctl enable rfsite-cloud-api"
    echo "4. Start service: sudo systemctl start rfsite-cloud-api"
else
    echo "Next steps:"
    echo "1. Review configuration: sudo nano $CONFIG_FILE"
    echo "2. Restart service: sudo systemctl restart rfsite-cloud-api"
fi
echo "3. Check status: sudo systemctl status rfsite-cloud-api"
echo "4. View logs: sudo journalctl -u rfsite-cloud-api -f"
echo ""
echo "The API will be available at the configured host:port (default: 127.0.0.1:8001)"
