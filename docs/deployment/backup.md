# System-Level Backup and Recovery

This guide covers system-level backup strategies for production Trunk8 deployments, including infrastructure backup, disaster recovery, and data protection.

!!! note "Backup Types"
    This guide covers **system-level backups** for production deployments. For the built-in backup/restore feature accessible through the web interface, see the [User Guide Backup and Restore](../user-guide/backup-restore.md).

## What to Backup

### Essential System Files

**Application Data:**

- `config/config.toml` - Application configuration
- `users/` directory - Complete multi-user data structure
- `users/users.toml` - User management data
- `users/{username}/links.toml` - Per-user link data
- `users/{username}/assets/` - User-uploaded files

**Environment Configuration:**

- `.env` file - Environment variables (if used)
- Web server configuration (Nginx, Apache)
- SSL certificates
- Systemd/supervisor service files

**Optional System Files:**

- Application logs
- Database files (if using future database support)
- Custom themes or modifications

### What NOT to Backup

- Virtual environment (`.venv/`)
- Python cache files (`__pycache__/`)
- Log files (unless specifically needed)
- Temporary files

## System Backup Strategies

### 1. File-Based Backups

#### Simple Backup Script

```bash
#!/bin/bash
# /opt/trunk8-backup.sh

BACKUP_DIR="/backups/trunk8"
APP_DIR="/opt/trunk8"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="trunk8_system_backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup application data
echo "Backing up application data..."
cp -r "$APP_DIR/config" "$BACKUP_DIR/$BACKUP_NAME/"
cp -r "$APP_DIR/users" "$BACKUP_DIR/$BACKUP_NAME/"

# Backup environment file if it exists
if [ -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env" "$BACKUP_DIR/$BACKUP_NAME/"
fi

# Backup web server config
if [ -f "/etc/nginx/sites-available/trunk8" ]; then
    mkdir -p "$BACKUP_DIR/$BACKUP_NAME/nginx"
    cp "/etc/nginx/sites-available/trunk8" "$BACKUP_DIR/$BACKUP_NAME/nginx/"
fi

# Create compressed archive
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "trunk8_system_backup_*.tar.gz" -mtime +30 -delete

echo "System backup completed: ${BACKUP_NAME}.tar.gz"
```

#### Automated Scheduling

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/trunk8-backup.sh

# Weekly backup to external storage
0 3 * * 0 /opt/trunk8-backup.sh && /opt/sync-to-cloud.sh
```

### 2. Container Backups

For Docker deployments:

```bash
#!/bin/bash
# Docker backup script

BACKUP_DIR="/backups/trunk8"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup volumes
docker run --rm \
  -v trunk8-config:/config \
  -v trunk8-users:/users \
  -v "$BACKUP_DIR:/backup" \
  alpine tar czf "/backup/trunk8_docker_$DATE.tar.gz" /config /users

# Backup container configuration
docker-compose config > "$BACKUP_DIR/docker-compose_$DATE.yml"
```

## Off-site Backup Solutions

### Cloud Storage Integration

#### AWS S3

```bash
#!/bin/bash
# S3 backup sync script

LOCAL_BACKUP_DIR="/backups/trunk8"
S3_BUCKET="s3://your-backup-bucket/trunk8"

# Install AWS CLI
aws configure

# Sync backups to S3
aws s3 sync "$LOCAL_BACKUP_DIR" "$S3_BUCKET" \
  --exclude "*.tmp" \
  --storage-class STANDARD_IA

# Lifecycle policy for old backups
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-backup-bucket \
  --lifecycle-configuration file://lifecycle.json
```

#### Rclone (Multi-Cloud)

```bash
#!/bin/bash
# Rclone backup script

# Configure rclone
rclone config

# Sync to multiple cloud providers
rclone sync /backups/trunk8 gdrive:trunk8-backups
rclone sync /backups/trunk8 dropbox:trunk8-backups
rclone sync /backups/trunk8 onedrive:trunk8-backups
```

### Rsync to Remote Server

```bash
#!/bin/bash
# Remote server backup

REMOTE_SERVER="backup-server.example.com"
REMOTE_PATH="/srv/backups/trunk8"
LOCAL_PATH="/backups/trunk8"

# Sync via SSH
rsync -avz --delete \
  -e "ssh -i /root/.ssh/backup_key" \
  "$LOCAL_PATH/" \
  "backup@$REMOTE_SERVER:$REMOTE_PATH/"
```

## Disaster Recovery Procedures

### Complete System Recovery

#### 1. Fresh System Setup

```bash
# Install dependencies
sudo apt update && sudo apt install -y python3.12 python3.12-venv git nginx

# Create application user
sudo useradd -m -s /bin/bash trunk8

# Clone application
sudo -u trunk8 git clone https://github.com/lancereinsmith/trunk8.git /opt/trunk8
```

#### 2. Restore Application Data

```bash
# Extract backup
cd /tmp
tar -xzf trunk8_system_backup_20240622_140000.tar.gz

# Restore configuration
sudo cp -r trunk8_system_backup_20240622_140000/config /opt/trunk8/
sudo cp -r trunk8_system_backup_20240622_140000/users /opt/trunk8/

# Restore environment
sudo cp trunk8_system_backup_20240622_140000/.env /opt/trunk8/

# Set permissions
sudo chown -R trunk8:trunk8 /opt/trunk8
sudo chmod 600 /opt/trunk8/.env
sudo chmod -R 600 /opt/trunk8/config/
sudo chmod -R 600 /opt/trunk8/users/
```

#### 3. Restore System Configuration

```bash
# Restore Nginx config
sudo cp trunk8_system_backup_20240622_140000/nginx/trunk8 /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/trunk8 /etc/nginx/sites-enabled/

# Restore SSL certificates (if backed up)
sudo cp -r trunk8_system_backup_20240622_140000/ssl/ /etc/ssl/trunk8/

# Restart services
sudo systemctl restart nginx
sudo systemctl restart trunk8  # If using systemd service
```

### Partial Recovery

#### Configuration Only

```bash
# Restore just configuration files
tar -xzf backup.tar.gz trunk8_system_backup_*/config/
sudo cp -r trunk8_system_backup_*/config/* /opt/trunk8/config/
```

#### User Data Only

```bash
# Restore specific user's data
tar -xzf backup.tar.gz trunk8_system_backup_*/users/username/
sudo cp -r trunk8_system_backup_*/users/username/ /opt/trunk8/users/
```

## Monitoring and Verification

### Backup Health Checks

```bash
#!/bin/bash
# Backup verification script

BACKUP_DIR="/backups/trunk8"
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/trunk8_system_backup_*.tar.gz | head -1)

# Check if backup exists and is recent
if [ -f "$LATEST_BACKUP" ]; then
    BACKUP_AGE=$(stat -c %Y "$LATEST_BACKUP")
    CURRENT_TIME=$(date +%s)
    AGE_HOURS=$(( (CURRENT_TIME - BACKUP_AGE) / 3600 ))
    
    if [ $AGE_HOURS -lt 48 ]; then
        echo "✓ Recent backup found: $LATEST_BACKUP"
    else
        echo "⚠ Backup is $AGE_HOURS hours old"
    fi
else
    echo "✗ No backups found"
fi

# Verify backup integrity
if tar -tzf "$LATEST_BACKUP" > /dev/null 2>&1; then
    echo "✓ Backup integrity verified"
else
    echo "✗ Backup integrity check failed"
fi
```

### Automated Monitoring

```bash
#!/bin/bash
# Send backup status via email

BACKUP_STATUS=$(/opt/backup-check.sh)

if echo "$BACKUP_STATUS" | grep -q "✗"; then
    echo "$BACKUP_STATUS" | mail -s "Trunk8 Backup Issue" admin@example.com
fi
```

## Security Considerations

### Backup Encryption

```bash
# Encrypt backups with GPG
gpg --symmetric --cipher-algo AES256 backup.tar.gz

# Decrypt when needed
gpg --output backup.tar.gz --decrypt backup.tar.gz.gpg
```

### Access Control

```bash
# Secure backup directory permissions
sudo chown -R root:backup /backups/trunk8
sudo chmod -R 750 /backups/trunk8

# Secure backup scripts
sudo chmod 700 /opt/trunk8-backup.sh
```

## Integration with Built-in Backup

The system-level backups complement Trunk8's built-in backup feature:

| Backup Type | Use Case | Frequency | Scope |
|-------------|----------|-----------|-------|
| **Built-in** | User data portability | On-demand | Per-user data |
| **System-level** | Disaster recovery | Automated | Complete system |

### Backup Strategy Matrix

- **Built-in backups**: User migration, data portability
- **System backups**: Infrastructure protection, disaster recovery
- **Both**: Complete protection strategy

## Compliance and Retention

### Regulatory Requirements

- **GDPR**: Right to data portability (built-in backup feature)
- **SOX**: Data retention requirements (system backups)
- **HIPAA**: Secure backup requirements (encryption)

### Documentation Requirements

- Backup procedures documentation
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)
- Incident response procedures

## Next Steps

- Set up [Production Deployment](production.md) with backup strategy
- Implement [Security Considerations](security.md) for backup protection
- Configure [Performance Monitoring](performance.md) including backup health
- Review [User Guide Backup Feature](../user-guide/backup-restore.md) for user-level operations 