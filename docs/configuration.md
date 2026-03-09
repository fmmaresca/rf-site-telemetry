# Configuration

The RF Site Telemetry Cloud API supports flexible configuration through YAML files and environment variables.

## Configuration Priority

1. **Environment variables** (highest priority)
2. **YAML configuration file**
3. **Default values** (lowest priority)

## Configuration File

The default configuration file location is `/etc/rfsite/cloud-api.yaml`. You can override this with the `CONFIG_FILE` environment variable.

### Example Configuration

```yaml
# Database connection
db_dsn: "postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry"

# Authentication settings
auth_required: true
public_readonly_tenant: null  # e.g. "demo" for public access

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file_path: "/var/log/rfsite/cloud-api.log"
  max_bytes: 10485760  # 10MB per file
  backup_count: 30  # Keep 30 days of logs
```

## Environment Variables

All configuration options can be overridden with environment variables:

- `CONFIG_FILE` - Path to YAML config file
- `DB_DSN` - Database connection string
- `AUTH_REQUIRED` - Enable/disable authentication (true/false)
- `PUBLIC_READONLY_TENANT` - Public tenant name for read-only access
- `LOGGING__LEVEL` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOGGING__FILE_PATH` - Log file path

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

For local development, you can use environment variables or a local config file:

```bash
# Using environment variables
export DB_DSN='postgresql://rftelemetry:rftelemetry@localhost:5432/rftelemetry'
export AUTH_REQUIRED=0
export LOGGING__FILE_PATH='./logs/cloud-api.log'

# Or using a config file
export CONFIG_FILE='./config.dev.yaml'
```

## Production Deployment

1. Copy the example config:
   ```bash
   sudo cp cloud-api/config.example.yaml /etc/rfsite/cloud-api.yaml
   ```

2. Edit the configuration:
   ```bash
   sudo nano /etc/rfsite/cloud-api.yaml
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
