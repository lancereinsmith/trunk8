#!/usr/bin/env bash
# install-lightsail.sh — Deploy Trunk8 on AWS Lightsail (Ubuntu 22.04/24.04)
set -euo pipefail

APP_DIR="/opt/trunk8"
APP_USER="trunk8"
APP_GROUP="trunk8"
REPO_URL="https://github.com/lancereinsmith/trunk8.git"
GUNICORN_BIND="127.0.0.1:5001"
GUNICORN_WORKERS=2

# ---------- helpers ----------
info()  { printf '\033[1;34m[INFO]\033[0m  %s\n' "$1"; }
warn()  { printf '\033[1;33m[WARN]\033[0m  %s\n' "$1"; }
error() { printf '\033[1;31m[ERROR]\033[0m %s\n' "$1" >&2; exit 1; }

# ---------- pre-checks ----------
[[ $EUID -eq 0 ]] || error "This script must be run as root (use sudo)."

if ! grep -qi 'ubuntu' /etc/os-release 2>/dev/null; then
    warn "This script is designed for Ubuntu. Proceed at your own risk."
fi

# ---------- prompt for config ----------
read -rp "Domain name (leave blank for IP-only access): " DOMAIN
read -rsp "Admin password for Trunk8: " ADMIN_PASSWORD
echo
[[ -n "$ADMIN_PASSWORD" ]] || error "Admin password cannot be empty."

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# ---------- system packages ----------
info "Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv nginx certbot python3-certbot-nginx git curl > /dev/null

# ---------- firewall ----------
info "Configuring firewall (ufw)..."
if command -v ufw &>/dev/null; then
    ufw allow OpenSSH > /dev/null 2>&1 || true
    ufw allow 'Nginx Full' > /dev/null 2>&1 || true
    ufw --force enable > /dev/null 2>&1 || true
fi

# ---------- service user ----------
info "Creating service user '${APP_USER}'..."
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER"
fi

# ---------- clone repo ----------
info "Cloning repository to ${APP_DIR}..."
if [[ -d "$APP_DIR" ]]; then
    warn "${APP_DIR} already exists — pulling latest changes."
    git -C "$APP_DIR" pull --ff-only || warn "Git pull failed; using existing code."
else
    git clone "$REPO_URL" "$APP_DIR"
fi
chown -R "${APP_USER}:${APP_GROUP}" "$APP_DIR"

# ---------- install uv ----------
info "Installing uv..."
if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh > /dev/null 2>&1
fi

# ---------- install app deps ----------
info "Installing application dependencies..."
cd "$APP_DIR"
sudo -u "$APP_USER" uv sync --no-dev --frozen

# ---------- configure .env ----------
info "Writing .env configuration..."
cat > "${APP_DIR}/.env" <<EOF
TRUNK8_ADMIN_PASSWORD=${ADMIN_PASSWORD}
TRUNK8_SECRET_KEY=${SECRET_KEY}
TRUNK8_LOG_LEVEL=INFO
TRUNK8_PORT=5001
EOF
chown "${APP_USER}:${APP_GROUP}" "${APP_DIR}/.env"
chmod 600 "${APP_DIR}/.env"

# ---------- systemd service ----------
info "Creating systemd service..."
cat > /etc/systemd/system/trunk8.service <<EOF
[Unit]
Description=Trunk8 Link Shortener
After=network.target

[Service]
Type=notify
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/gunicorn run:app \\
    --bind ${GUNICORN_BIND} \\
    --workers ${GUNICORN_WORKERS} \\
    --timeout 120 \\
    --access-logfile - \\
    --error-logfile -
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# ---------- nginx ----------
info "Configuring nginx..."
SERVER_NAME="${DOMAIN:-_}"
cat > /etc/nginx/sites-available/trunk8 <<EOF
server {
    listen 80;
    server_name ${SERVER_NAME};

    location / {
        proxy_pass http://${GUNICORN_BIND};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/trunk8 /etc/nginx/sites-enabled/trunk8
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# ---------- SSL ----------
if [[ -n "$DOMAIN" ]]; then
    info "Requesting SSL certificate for ${DOMAIN}..."
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email || \
        warn "Certbot failed. You can retry later with: certbot --nginx -d ${DOMAIN}"
else
    warn "No domain provided — skipping SSL setup."
fi

# ---------- start service ----------
info "Starting Trunk8..."
systemctl enable --now trunk8

# ---------- verify ----------
sleep 2
if curl -sf "http://${GUNICORN_BIND}/" > /dev/null 2>&1; then
    info "Trunk8 is running."
else
    warn "Service may not be ready yet. Check: systemctl status trunk8"
fi

# ---------- summary ----------
echo
echo "============================================"
echo "  Trunk8 installation complete!"
echo "============================================"
if [[ -n "$DOMAIN" ]]; then
    echo "  URL:      https://${DOMAIN}"
else
    echo "  URL:      http://<your-server-ip>"
fi
echo "  App dir:  ${APP_DIR}"
echo "  Service:  systemctl {start|stop|restart|status} trunk8"
echo "  Logs:     journalctl -u trunk8 -f"
echo "  .env:     ${APP_DIR}/.env"
echo "============================================"
echo
echo "Next steps:"
echo "  - Upload your config.toml to ${APP_DIR}/config.toml"
if [[ -z "$DOMAIN" ]]; then
    echo "  - Set up a domain and run: certbot --nginx -d yourdomain.com"
fi
echo "  - Open Lightsail networking tab and allow ports 80 & 443"
echo
