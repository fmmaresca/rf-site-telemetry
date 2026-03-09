# Configuration

The RF Site Telemetry Cloud API uses a single YAML configuration file.

## Configuration File

The default configuration file location is `/etc/rfsite-cloud-api/config.yaml`. You can specify a different location using the `--config` command line option.

### Example Configuration

```yaml
# Database connection
db_dsn: "postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry"

# Authentication settings
auth_required: true
public_readonly_tenant: null  # e.g. "demo" for public access

# Server settings
host: "127.0.0.1"
port: 8001

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file_path: "/var/log/rfsite/cloud-api.log"
  max_bytes: 10485760  # 10MB per file
  backup_count: 30  # Keep 30 days of logs
```

## Command Line Options

- `--config` - Path to YAML config file (default: `/etc/rfsite-cloud-api/config.yaml`)

## Logging

The API uses daily log rotation with the following features:

- **Daily rotation**: New log file created at midnight
- **Configurable retention**: Default 30 days
- **Structured format**: Timestamp, logger name, level, message
- **Dual output**: Both file and console (for development)

### Log File Locations

- **Production**: `/var/log/rfsite/cloud-api.log`
- **Development**: `./logs/cloud-api.log` (or configure as needed)

### Log Rotation

Log files are automatically rotated daily with the format:
- `cloud-api.log` (current)
- `cloud-api.log.2024-03-09` (previous days)

## Development Setup

For local development, create a local config file:

```bash
# Create a development config file
cp cloud-api/config.example.yaml config.dev.yaml

# Edit for development
nano config.dev.yaml

# Run with custom config
rfsite-cloud-api --config config.dev.yaml
```

## Production Deployment

1. Copy the example config:
   ```bash
   sudo mkdir -p /etc/rfsite-cloud-api
   sudo cp cloud-api/config.example.yaml /etc/rfsite-cloud-api/config.yaml
   ```

2. Edit the configuration:
   ```bash
   sudo nano /etc/rfsite-cloud-api/config.yaml
   ```

3. Create log directory:
   ```bash
   sudo mkdir -p /var/log/rfsite
   sudo chown www-data:www-data /var/log/rfsite
   ```

4. Start the service:
   ```bash
   sudo systemctl enable rfsite-cloud-api
   sudo systemctl start rfsite-cloud-api
   ```
