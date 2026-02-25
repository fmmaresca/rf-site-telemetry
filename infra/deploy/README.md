
# 1) crear dirs
sudo mkdir -p /opt/rfsite
sudo mkdir -p /etc/rfsite-cloud-api

# 2) code (ejemplo: git clone)
sudo git clone <tu_repo> /opt/rfsite
# o rsync del subdir cloud-api a /opt/rfsite/cloud-api

# 3) venv
sudo python3 -m venv /opt/rfsite/venv
sudo /opt/rfsite/venv/bin/pip install -U pip
sudo /opt/rfsite/venv/bin/pip install -e /opt/rfsite/cloud-api

# 4) env
sudo cp infra/deploy/env.example /etc/rfsite-cloud-api/env
sudo nano /etc/rfsite-cloud-api/env

# 5) systemd unit
sudo cp infra/deploy/systemd/rfsite-cloud-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rfsite-cloud-api

# 6) nginx site
sudo cp infra/deploy/nginx/rfsite-cloud-api.conf /etc/nginx/sites-available/rfsite-cloud-api
sudo ln -sf /etc/nginx/sites-available/rfsite-cloud-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 7) migraciones
psql "$DB_DSN" -f infra/migrations/001_init.sql
