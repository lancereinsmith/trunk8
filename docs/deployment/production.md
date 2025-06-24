# Production Deployment

This guide covers best practices for deploying Trunk8 in production environments.

## Overview

Production deployments require careful consideration of:

- Performance optimization
- Security hardening
- High availability
- Monitoring and logging
- Backup strategies

## Deployment Options

### Option 1: Traditional Server Deployment

Deploy on a VPS or dedicated server with:

- Ubuntu 22.04 LTS or similar
- Python 3.12+
- Nginx as reverse proxy
- Supervisor for process management

### Option 2: Docker Deployment

See the [Docker Deployment Guide](../getting-started/docker.md) for containerized deployment.

### Option 3: Platform-as-a-Service

Deploy on PaaS providers:

- Heroku
- Railway
- Render
- DigitalOcean App Platform

## Server Setup

### 1. System Requirements

Minimum requirements:

- 1 CPU core
- 1GB RAM
- 10GB storage
- Ubuntu 22.04 LTS

Recommended for production:

- 2+ CPU cores
- 2GB+ RAM
- 50GB+ storage
- Load balancer ready

### 2. Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip nginx supervisor git

# Create application user
sudo useradd -m -s /bin/bash trunk8
sudo usermod -aG www-data trunk8
```

### 3. Application Setup

```bash
# Switch to trunk8 user
sudo su - trunk8

# Clone repository
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
pip install gunicorn
```

### 4. Environment Configuration

Create `/home/trunk8/trunk8/.env`:

```bash
TRUNK8_ADMIN_PASSWORD=your-very-secure-password
TRUNK8_SECRET_KEY=your-secret-key-here
```

## Web Server Configuration

### Nginx Setup

Create `/etc/nginx/sites-available/trunk8`:

```nginx
upstream trunk8 {
    server unix:/home/trunk8/trunk8/trunk8.sock;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy configuration
    location / {
        proxy_pass http://trunk8;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static {
        alias /home/trunk8/trunk8/app/static;
        expires 30d;
    }

    # Upload limit
    client_max_body_size 50M;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/trunk8 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate

Use Let's Encrypt for free SSL:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Process Management

### Supervisor Configuration

Create `/etc/supervisor/conf.d/trunk8.conf`:

```ini
[program:trunk8]
command=/home/trunk8/trunk8/venv/bin/gunicorn run:app --bind unix:/home/trunk8/trunk8/trunk8.sock --workers 4 --timeout 120
directory=/home/trunk8/trunk8
user=trunk8
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/trunk8/trunk8.log
environment=PATH="/home/trunk8/trunk8/venv/bin",TRUNK8_ADMIN_PASSWORD="%(ENV_TRUNK8_ADMIN_PASSWORD)s",TRUNK8_SECRET_KEY="%(ENV_TRUNK8_SECRET_KEY)s"
```

Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start trunk8
```

## Performance Optimization

### Gunicorn Workers

Calculate optimal workers:
```python
workers = (2 * cpu_cores) + 1
```

### Caching

Configure Nginx caching for static assets:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Monitoring

### Application Monitoring

1. **Health Check Endpoint**
   ```python
   @app.route('/health')
   def health():
       return {'status': 'healthy'}, 200
   ```

2. **Prometheus Metrics**
   ```bash
   pip install prometheus-flask-exporter
   ```

3. **Application Performance Monitoring**
    - Sentry for error tracking
    - New Relic for performance
    - DataDog for infrastructure

### Log Management

Configure centralized logging:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/trunk8.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Uptime Monitoring

Use external monitoring services:

- UptimeRobot
- Pingdom
- StatusCake

## Backup Strategy

### Automated Backups

Create backup script `/home/trunk8/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/trunk8/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration and assets
tar -czf $BACKUP_DIR/trunk8_backup_$DATE.tar.gz \
    /home/trunk8/trunk8/config/config.toml \
    /home/trunk8/trunk8/links.toml \
    /home/trunk8/trunk8/assets/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "trunk8_backup_*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 3 * * * /home/trunk8/backup.sh
```

### Off-site Backups

Sync to cloud storage:
```bash
# Install rclone
curl https://rclone.org/install.sh | sudo bash

# Configure cloud storage
rclone config

# Sync backups
rclone sync /home/trunk8/backups remote:trunk8-backups
```

## Scaling Strategies

### Horizontal Scaling

1. **Load Balancer**
    - HAProxy
    - Nginx upstream
    - Cloud load balancers

2. **Shared Storage**
    - NFS for assets
    - S3-compatible storage
    - GlusterFS

3. **Session Storage**
    - Redis for sessions
    - Memcached
    - Database sessions

### Vertical Scaling

Monitor and upgrade:

- CPU utilization
- Memory usage
- Disk I/O
- Network bandwidth

## Security Hardening

See the [Security Guide](security.md) for comprehensive security practices.

Key points:

- Regular security updates
- Firewall configuration
- Intrusion detection
- Security scanning

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
    - Check Gunicorn is running
    - Verify socket permissions
    - Review Nginx error logs

2. **Slow Performance**
    - Increase Gunicorn workers
    - Enable Nginx caching
    - Optimize file serving

3. **High Memory Usage**
    - Limit Gunicorn workers
    - Configure swap space
    - Monitor for memory leaks

## Next Steps

- Implement [Security Best Practices](security.md)
- Set up [Backup and Recovery](backup.md)
- Configure [Performance Monitoring](performance.md)
- Plan for [High Availability](../reference/faq.md#advanced) 