# Environment Variables

Trunk8 uses environment variables for sensitive configuration that shouldn't be stored in files.

## Available Environment Variables

### TRUNK8_ADMIN_PASSWORD

**Purpose**: Sets the admin password for accessing protected features.

**Default**: `admin` (change this in production!)

**Example**:
```bash
export TRUNK8_ADMIN_PASSWORD="my-very-secure-password-123"
```

### TRUNK8_SECRET_KEY

**Purpose**: Secret key for Flask session encryption and security.

**Default**: Random value generated at runtime

**Example**:
```bash
export TRUNK8_SECRET_KEY="your-secret-key-here-make-it-long-and-random"
```

**Generate a secure key**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### TRUNK8_PORT

**Purpose**: Sets the port number for the Flask development server.

**Default**: `5001`

**Example**:
```bash
# Run on port 8080
export TRUNK8_PORT="8080"

# Run on port 3000
export TRUNK8_PORT="3000"
```

**Note**: This only affects the development server started with `python run.py`. For production deployments with Gunicorn, specify the port using Gunicorn's `--bind` option:
```bash
gunicorn run:app --bind 0.0.0.0:8080
```

### TRUNK8_LOG_LEVEL

**Purpose**: Controls the verbosity of application logging output.

**Default**: `INFO`

**Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Example**:
```bash
# Set to DEBUG for detailed troubleshooting
export TRUNK8_LOG_LEVEL="DEBUG"

# Set to WARNING to only see warnings and errors
export TRUNK8_LOG_LEVEL="WARNING"
```

**Description**: 

- `DEBUG`: Verbose logging including detailed operational info
- `INFO`: General information about application operation (default)
- `WARNING`: Warning messages and above
- `ERROR`: Error messages and above
- `CRITICAL`: Only critical errors

**Log Format**: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`

## Setting Environment Variables

### Method 1: Shell Export

Set temporarily in current shell:
```bash
export TRUNK8_ADMIN_PASSWORD="secure-password"
export TRUNK8_SECRET_KEY="secret-key"
python run.py
```

### Method 2: .env File

Create a `.env` file in project root:
```env
# .env
TRUNK8_ADMIN_PASSWORD=secure-password
TRUNK8_SECRET_KEY=your-secret-key-here
TRUNK8_LOG_LEVEL=INFO
TRUNK8_PORT=5001
```

The application automatically loads this file using python-dotenv.

### Method 3: System Environment

Add to shell profile (`~/.bashrc`, `~/.zshrc`):
```bash
# Trunk8 Configuration
export TRUNK8_ADMIN_PASSWORD="secure-password"
export TRUNK8_SECRET_KEY="your-secret-key"
```

Reload profile:
```bash
source ~/.bashrc
```

### Method 4: Docker

Pass to Docker container:
```bash
docker run -p 5001:5001 \
  -e TRUNK8_ADMIN_PASSWORD="secure-password" \
  -e TRUNK8_SECRET_KEY="secret-key" \
  -e TRUNK8_LOG_LEVEL="INFO" \
  -e TRUNK8_PORT="5001" \
  trunk8
```

Using docker-compose:
```yaml
version: '3'
services:
  trunk8:
    image: trunk8
    ports:
      - "${TRUNK8_PORT:-5001}:${TRUNK8_PORT:-5001}"
    environment:
      - TRUNK8_ADMIN_PASSWORD=${TRUNK8_ADMIN_PASSWORD}
      - TRUNK8_SECRET_KEY=${TRUNK8_SECRET_KEY}
      - TRUNK8_PORT=${TRUNK8_PORT:-5001}
```

### Method 5: Systemd

For systemd services:
```ini
[Service]
Environment="TRUNK8_ADMIN_PASSWORD=secure-password"
Environment="TRUNK8_SECRET_KEY=secret-key"
```

### Method 6: Supervisor

In supervisor config:
```ini
[program:trunk8]
environment=TRUNK8_ADMIN_PASSWORD="%(ENV_TRUNK8_ADMIN_PASSWORD)s",TRUNK8_SECRET_KEY="%(ENV_TRUNK8_SECRET_KEY)s"
```

## Security Best Practices

### Password Requirements

Create strong admin passwords:

- Minimum 12 characters
- Mix of upper/lowercase letters
- Include numbers and symbols
- Unique to Trunk8

**Good Example**:
```bash
export TRUNK8_ADMIN_PASSWORD="Tr8nk!Secure#2024$Admin"
```

**Bad Examples**:

- `admin` (default)
- `password123`
- `trunk8`

### Secret Key Guidelines

The secret key should be:

- At least 32 characters
- Randomly generated
- Never shared or committed
- Unique per installation

**Generate secure keys**:
```python
# Option 1: Hex string
python -c "import secrets; print(secrets.token_hex(32))"

# Option 2: URL-safe string
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 3: UUID-based
python -c "import uuid; print(uuid.uuid4().hex + uuid.uuid4().hex)"
```

### File Permissions

Protect `.env` files:
```bash
# Restrict to owner only
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw-------
```

### Git Security

Never commit sensitive data:

Add to `.gitignore`:
```gitignore
# Environment variables
.env
.env.local
.env.production
```

## Verification

### Check if Variables are Set

```bash
# Check specific variable
echo $TRUNK8_ADMIN_PASSWORD

# Check all Trunk8 variables
env | grep TRUNK8_
```

### Test in Python

```python
import os

password = os.getenv('TRUNK8_ADMIN_PASSWORD', 'not-set')
secret_key = os.getenv('TRUNK8_SECRET_KEY', 'not-set')

print(f"Password configured: {'Yes' if password != 'not-set' else 'No'}")
print(f"Secret key configured: {'Yes' if secret_key != 'not-set' else 'No'}")
```

## Troubleshooting

### Variables Not Loading

1. **Check spelling** - Variable names are case-sensitive
2. **Verify .env location** - Must be in project root
3. **Restart application** - Changes require restart
4. **Check shell** - Some shells need `export` prefix

### Docker Issues

Variables not passing to container:
```bash
# Debug: Print environment in container
docker run --rm trunk8 env | grep TRUNK8_

# Fix: Use --env-file
docker run --env-file .env trunk8
```

### Permission Denied

If `.env` can't be read:
```bash
# Check ownership
ls -la .env

# Fix permissions
chmod 644 .env
```

## Advanced Usage

### Multiple Environments

Use different files per environment:
```bash
# Development
cp .env.development .env

# Staging
cp .env.staging .env

# Production
cp .env.production .env
```

### Dynamic Values

Generate values at runtime:
```bash
# In startup script
export TRUNK8_SECRET_KEY=$(openssl rand -hex 32)
```

### Validation Script

Create `check_env.py`:
```python
#!/usr/bin/env python3
import os
import sys

required_vars = ['TRUNK8_ADMIN_PASSWORD', 'TRUNK8_SECRET_KEY']
missing = []

for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print(f"Error: Missing environment variables: {', '.join(missing)}")
    sys.exit(1)
else:
    print("All required environment variables are set!")
```


## Security Checklist

- [ ] Changed default admin password
- [ ] Generated unique secret key
- [ ] Protected .env file permissions
- [ ] Added .env to .gitignore
- [ ] Documented variables for team
- [ ] Regular password rotation schedule
- [ ] Monitoring for exposed secrets

## Next Steps

- Review [Security Best Practices](../deployment/security.md)
- Configure [Application Settings](app-config.md)
- Set up [Production Deployment](../deployment/production.md)
- Learn about [Configuration Management](overview.md) 