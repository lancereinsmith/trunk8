# Security Considerations

This guide covers security best practices for deploying Trunk8 in production environments.

## Overview

While Trunk8 includes basic security features, production deployments require additional hardening. This guide covers:

- Authentication and authorization
- Network security
- Data protection
- Security monitoring
- Incident response

## Authentication Security

### Strong Admin Password

**Never use the default password in production!**

```bash
# Generate a strong password
openssl rand -base64 32

# Set in environment
export TRUNK8_ADMIN_PASSWORD="your-very-strong-password-here"
```

### Session Security

#### Secure Secret Key

Generate a cryptographically secure secret key:

```python
# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Set in environment:
```bash
export TRUNK8_SECRET_KEY="your-generated-secret-key"
```

#### Session Configuration

Configure secure session settings:

```toml
# config.toml
[app]
permanent_lifetime_days = 1  # Shorter sessions for sensitive environments
```

### Future Authentication Enhancements

Consider implementing:

- Password hashing with bcrypt
- Two-factor authentication (2FA)
- OAuth/SAML integration
- API key authentication

## Network Security

### HTTPS Configuration

**Always use HTTPS in production!**

#### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name trunk8.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/trunk8.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trunk8.example.com/privkey.pem;
    
    # Modern SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Additional security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name trunk8.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall Configuration

#### UFW (Ubuntu/Debian)

```bash
# Allow SSH (adjust port as needed)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

#### iptables

```bash
# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Drop all other inbound traffic
iptables -A INPUT -j DROP
```

### Rate Limiting

Protect against brute force attacks:

#### Nginx Rate Limiting

```nginx
# In http block
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;

# In server block
location /auth/login {
    limit_req zone=login burst=5 nodelay;
    proxy_pass http://localhost:5001;
}

location / {
    limit_req zone=general burst=20 nodelay;
    proxy_pass http://localhost:5001;
}
```

## Data Protection

### File Upload Security

#### Enhanced UUID4 Security

Trunk8 uses UUID4-based file naming for maximum security:

- **UUID4 Filenames**: Files stored as `f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf`
- **Original Filename Preservation**: Users see familiar names when downloading
- **Comprehensive Metadata**: File size, MIME type, upload date tracking
- **File Type Validation**: Configurable allowed extensions
- **Size Limits**: Configurable maximum file size (100MB default)

#### File Validation Configuration

```python
# Enhanced validation in secure_file_upload()
ALLOWED_EXTENSIONS = {
    # Documents
    'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
    # Images
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg',
    # Archives
    'zip', 'rar', '7z', 'tar', 'gz',
    # Spreadsheets
    'xls', 'xlsx', 'ods', 'csv',
    # Presentations
    'ppt', 'pptx', 'odp',
    # Audio/Video
    'mp3', 'wav', 'mp4', 'avi', 'mkv', 'mov',
    # Code
    'py', 'js', 'html', 'css', 'json', 'xml', 'md'
}

# Maximum file size is now configurable in config/config.toml
# Default: max_file_size_mb = 100  # 100MB
```

#### Security Benefits

- **Prevents Enumeration**: UUID4 names make file discovery impossible
- **No Information Leakage**: Original filenames hidden from URLs
- **Collision-Free**: Cryptographically unique filenames
- **Audit Trail**: Upload metadata for monitoring and compliance

#### Example Metadata Storage

```toml
[links.report]
type = "file"
path = "f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf"
original_filename = "Q4-Financial-Report-2024.pdf"
file_size = 2048576
mime_type = "application/pdf"
upload_date = "2024-01-15T10:30:00"
```

#### File Size Limits

Configure in Nginx:

```nginx
# Limit upload size (adjust based on your max_file_size_mb config)
client_max_body_size 100M;
```

#### Virus Scanning

Integrate ClamAV for uploaded files:

```bash
# Install ClamAV
sudo apt-get install clamav clamav-daemon

# Python integration
pip install pyclamd
```

### Input Validation

#### XSS Prevention

- Flask auto-escapes template variables
- Validate all user input
- Sanitize markdown content


### Secure File Storage

#### Directory Permissions

```bash
# Restrict access to config files
chmod 600 config/config.toml users/users.toml
chmod -R 600 users/*/links.toml

# Secure user assets directories
chmod 750 users/*/assets/
chown -R www-data:www-data users/*/assets/
```

#### User Data Isolation

Files are automatically organized by user:

```toml
# Multi-user assets are automatically organized
users/
├── admin/assets/    # Admin files
├── john/assets/     # John's files
└── mary/assets/     # Mary's files
```

## Access Control

### IP Whitelisting

Restrict admin access by IP:

```nginx
location /auth/login {
    allow 192.168.1.0/24;  # Local network
    allow 203.0.113.5;     # Admin IP
    deny all;
    
    proxy_pass http://localhost:5001;
}
```

### Fail2Ban Integration

Protect against brute force:

```ini
# /etc/fail2ban/jail.local
[trunk8-auth]
enabled = true
port = http,https
filter = trunk8-auth
logpath = /var/log/nginx/access.log
maxretry = 5
bantime = 3600

# /etc/fail2ban/filter.d/trunk8-auth.conf
[Definition]
failregex = ^<HOST> .* "POST /auth/login HTTP/.*" 401
ignoreregex =
```

## Security Headers

### Content Security Policy

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com;" always;
```

### Permissions Policy

```nginx
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

## Monitoring and Logging

### Application Logging

Configure comprehensive logging:

```python
import logging

logging.basicConfig(
    filename='/var/log/trunk8/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

### Security Monitoring

#### Log Analysis

Monitor for:

- Failed login attempts
- Unusual file uploads
- Suspicious short codes
- Rate limit violations

#### Alerting

Set up alerts for:

- Multiple failed logins
- Large file uploads
- Disk space issues
- Service downtime

### Audit Trail

Track administrative actions:

```python
def log_admin_action(action, details):
    """Log administrative actions for audit trail."""
    app.logger.info(f"ADMIN ACTION: {action} - {details}")
```

### Detection

Monitor for indicators:

- Unexpected files in user assets directories
- Modified configuration files
- Unusual network traffic
- System resource spikes


## Security Checklist

### Pre-Deployment

- [ ] Strong admin password set
- [ ] Secret key configured
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] File permissions set
- [ ] UUID4 file security enabled
- [ ] Backups configured
]

## Additional Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/latest/security/)
- [Let's Encrypt](https://letsencrypt.org/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/) 