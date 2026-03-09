# Deployment

This document covers production deployment of the RF Site Telemetry system.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- PostgreSQL 13+
- Python 3.11+
- nginx (for reverse proxy)
- systemd (for service management)

## Quick Installation

1. Clone repository:
   ```bash
   git clone <repository-url>
   cd rf-site-telemetry
   ```

2. Run installation script:
   ```bash
   sudo ./infra/deploy/install.sh
   ```

3. Configure the API:
   ```bash
   sudo nano /etc/rfsite-cloud-api/config.yaml
   ```

4. Start the service:
   ```bash
   sudo systemctl enable rfsite-cloud-api
   sudo systemctl start rfsite-cloud-api
   ```

## Manual Installation

### Database Setup

1. Install PostgreSQL:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. Create database and user:
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE rftelemetry;
   CREATE USER rftelemetry WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE rftelemetry TO rftelemetry;
   \q
   ```

3. Run migrations:
   ```bash
   psql -h localhost -U rftelemetry -d rftelemetry -f infra/migrations/0001_init.sql
   psql -h localhost -U rftelemetry -d rftelemetry -f infra/migrations/0002_api_keys.sql
   ```

### Cloud API Manual Setup

1. Install system dependencies:
   ```bash
   sudo apt install python3 python3-venv python3-pip
   ```

2. Create directories:
   ```bash
   sudo mkdir -p /opt/rfsite
   sudo mkdir -p /etc/rfsite-cloud-api
   sudo mkdir -p /var/log/rfsite
   ```

3. Copy source code:
   ```bash
   sudo cp -r cloud-api/* /opt/rfsite/
   sudo chown -R www-data:www-data /opt/rfsite
   ```

4. Create virtual environment:
   ```bash
   sudo -u www-data python3 -m venv /opt/rfsite/.venv
   sudo -u www-data /opt/rfsite/.venv/bin/pip install --upgrade pip
   sudo -u www-data /opt/rfsite/.venv/bin/pip install -e /opt/rfsite
   ```

5. Setup configuration:
   ```bash
   sudo cp /opt/rfsite/config.example.yaml /etc/rfsite-cloud-api/config.yaml
   sudo chown www-data:www-data /var/log/rfsite
   ```

6. Install systemd service:
   ```bash
   sudo cp infra/deploy/systemd/rfsite-cloud-api.service /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

## Configuration

Edit the main configuration file:

```bash
sudo nano /etc/rfsite-cloud-api/config.yaml
```

Key settings to configure:
- `db_dsn`: PostgreSQL connection string
- `auth_required`: Set to `false` for development
- `host`/`port`: Server binding
- `logging.file_path`: Log file location

## Service Management

```bash
# Enable auto-start
sudo systemctl enable rfsite-cloud-api

# Start service
sudo systemctl start rfsite-cloud-api

# Check status
sudo systemctl status rfsite-cloud-api

# View logs
sudo journalctl -u rfsite-cloud-api -f

# Restart service
sudo systemctl restart rfsite-cloud-api
```

## Testing Installation

1. Check service status:
   ```bash
   sudo systemctl status rfsite-cloud-api
   ```

2. Test API endpoints:
   ```bash
   curl http://127.0.0.1:8001/healthz
   curl http://127.0.0.1:8001/readyz
   ```

3. Check logs:
   ```bash
   sudo tail -f /var/log/rfsite/cloud-api.log
   ```

## Nginx Configuration

1. Install nginx:
   ```bash
   sudo apt install nginx
   ```

2. Copy configuration:
   ```bash
   sudo cp infra/deploy/nginx/rfsite-cloud-api.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/rfsite-cloud-api.conf /etc/nginx/sites-enabled/
   ```

3. Test and reload:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## SSL/TLS Setup

Use Let's Encrypt for SSL certificates:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## API Key Management

Create API keys for devices:

```bash
cd /opt/rfsite
.venv/bin/python tools/api_keys/create_api_key.py --tenant your-tenant --device-id device-001
```

## Monitoring

### Service Status

```bash
sudo systemctl status rfsite-cloud-api
```

### Logs

```bash
# Service logs
sudo journalctl -u rfsite-cloud-api -f

# Application logs
sudo tail -f /var/log/rfsite/cloud-api.log
```

### Health Checks

```bash
curl https://your-domain.com/healthz
curl https://your-domain.com/readyz
```

## Backup

### Database Backup

```bash
pg_dump -h localhost -U rftelemetry rftelemetry > backup.sql
```

### Configuration Backup

```bash
sudo cp /etc/rfsite-cloud-api/config.yaml /backup/location/
```

## Troubleshooting

### Service Won't Start

1. Check configuration:
   ```bash
   sudo /opt/rfsite/.venv/bin/rfsite-cloud-api --config /etc/rfsite-cloud-api/config.yaml
   ```

2. Check logs:
   ```bash
   sudo journalctl -u rfsite-cloud-api -n 50
   ```

### Database Connection Issues

1. Test connection:
   ```bash
   psql -h localhost -U rftelemetry -d rftelemetry -c "SELECT 1;"
   ```

2. Check firewall:
   ```bash
   sudo ufw status
   ```

### Permission Issues

```bash
sudo chown -R www-data:www-data /opt/rfsite
sudo chown -R www-data:www-data /var/log/rfsite
```

### Manual Testing

Test the API directly:

```bash
# Test with custom config
/opt/rfsite/.venv/bin/rfsite-cloud-api --config /etc/rfsite-cloud-api/config.yaml

# Test configuration loading
sudo -u www-data /opt/rfsite/.venv/bin/rfsite-cloud-api --config /etc/rfsite-cloud-api/config.yaml
```

## Reverse proxy

The public site serves the dashboard at `/` and proxies the API under `/api/`.

Nginx configuration key points:

- `proxy_pass http://127.0.0.1:8001;`
- SPA fallback must **exclude** `/api/` and `/assets/`

## Cloudflare caching

If you use Cloudflare in front, ensure that `/api/*` is **not cached**.

Recommended:

- Cache rule: *Bypass cache* for `URI path starts with /api/`
- Cache rule: *Cache* for `/assets/*` (hashed assets)
