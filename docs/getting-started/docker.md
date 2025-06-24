# Docker Deployment

Deploy Trunk8 using Docker for easy installation and management. This guide covers building, running, and configuring Trunk8 in Docker containers.

## Quick Start

### Pull and Run

The fastest way to get started:

```bash
docker run -p 5001:5001 ghcr.io/lancereinsmith/trunk8:latest
```

Access Trunk8 at `http://localhost:5001`.

### Build from Source

Clone and build the Docker image:

```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
docker build -t trunk8 .
```

Run the container:

```bash
docker run -p 5001:5001 trunk8
```

## Docker Image Details

The Trunk8 Docker image uses:

- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- **Package Manager**: uv for fast dependency installation
- **Web Server**: Gunicorn
- **Port**: 5001 (exposed and served)

## Configuration

### Environment Variables

Configure Trunk8 using environment variables:

```bash
docker run -p 5001:5001 \
  -e TRUNK8_ADMIN_PASSWORD="your-secure-password" \
  -e TRUNK8_SECRET_KEY="your-secret-key" \
  -e TRUNK8_PORT="5001" \
  trunk8
```

Available environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TRUNK8_ADMIN_PASSWORD` | Admin login password | `admin` |
| `TRUNK8_SECRET_KEY` | Flask session secret key | `your-secret-key-change-in-production` |
| `TRUNK8_PORT` | Port for Flask development server | `5001` |

### Using an .env File

Create a `.env` file:

```env
TRUNK8_ADMIN_PASSWORD=my-secure-password
TRUNK8_SECRET_KEY=my-secret-key-for-sessions
TRUNK8_PORT=5001
```

Run with the env file:

```bash
docker run -p 5001:5001 --env-file .env trunk8
```

## Persistent Storage

To persist data between container restarts, mount volumes for:

1. **User data** (`users/` directory containing user accounts and links)
2. **Configuration files** (`config/` directory containing app and theme settings)

### Using Docker Volumes

Create named volumes:

```bash
docker volume create trunk8-users
docker volume create trunk8-config
```

Run with volumes:

```bash
docker run -p 5001:5001 \
  -v trunk8-users:/app/users \
  -v trunk8-config:/app/config \
  trunk8
```

### Using Bind Mounts

Mount local directories:

```bash
docker run -p 5001:5001 \
  -v $(pwd)/users:/app/users \
  -v $(pwd)/config:/app/config \
  trunk8
```

## Docker Compose

For easier management, use Docker Compose:

### docker-compose.yml

```yaml
version: '3.8'

services:
  trunk8:
    image: ghcr.io/lancereinsmith/trunk8:latest
    ports:
      - "5001:5001"
    environment:
      - TRUNK8_ADMIN_PASSWORD=${TRUNK8_ADMIN_PASSWORD:-admin}
      - TRUNK8_SECRET_KEY=${TRUNK8_SECRET_KEY}
    volumes:
      - trunk8-users:/app/users
      - trunk8-config:/app/config
    restart: unless-stopped

volumes:
  trunk8-users:
  trunk8-config:
```

### Running with Docker Compose

Start the service:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

Stop the service:

```bash
docker-compose down
```

## Production Deployment

### Using a Reverse Proxy

For production, use a reverse proxy like Nginx:

#### nginx.conf

```nginx
server {
    listen 80;
    server_name trunk8.example.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS with Let's Encrypt

Use Certbot for automatic HTTPS:

```bash
sudo certbot --nginx -d trunk8.example.com
```

### Complete Production Stack

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  trunk8:
    image: ghcr.io/lancereinsmith/trunk8:latest
    environment:
      - TRUNK8_ADMIN_PASSWORD=${TRUNK8_ADMIN_PASSWORD}
      - TRUNK8_SECRET_KEY=${TRUNK8_SECRET_KEY}
    volumes:
      - trunk8-users:/app/users
      - trunk8-config:/app/config
    restart: always
    networks:
      - trunk8-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - certbot-etc:/etc/letsencrypt
      - certbot-var:/var/lib/letsencrypt
    depends_on:
      - trunk8
    restart: always
    networks:
      - trunk8-network

networks:
  trunk8-network:

volumes:
  trunk8-users:
  trunk8-config:
  certbot-etc:
  certbot-var:
```

## Backup and Restore

### Backup

Backup user data and configuration:

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup volumes
docker run --rm \
  -v trunk8-users:/users \
  -v trunk8-config:/config \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/$(date +%Y%m%d)/trunk8-backup.tar.gz /users /config
```

### Restore

Restore from backup:

```bash
# Restore volumes
docker run --rm \
  -v trunk8-users:/users \
  -v trunk8-config:/config \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/20240101/trunk8-backup.tar.gz -C /
```

## Container Management

### View Container Logs

```bash
docker logs trunk8
```

### Access Container Shell

```bash
docker exec -it trunk8 /bin/bash
```

### Monitor Resource Usage

```bash
docker stats trunk8
```

### Update Container

Pull the latest image and recreate:

```bash
docker pull ghcr.io/lancereinsmith/trunk8:latest
docker stop trunk8
docker rm trunk8
docker run -p 5001:5001 --name trunk8 ghcr.io/lancereinsmith/trunk8:latest
```

## Troubleshooting

### Container Won't Start

Check logs for errors:

```bash
docker logs trunk8
```

Common issues:
- Port 5001 already in use
- Permission issues with volumes
- Invalid environment variables

### Permission Issues

Fix volume permissions:

```bash
docker exec trunk8 chown -R 1000:1000 /app/assets
```

### Network Issues

Ensure the container can reach external services:

```bash
docker exec trunk8 ping -c 4 google.com
```

### Performance Tuning

Adjust Gunicorn workers in Dockerfile:

```dockerfile
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5001", "--workers", "8"]
```

## Security Considerations

1. **Always set secure passwords** for `TRUNK8_ADMIN_PASSWORD`
2. **Use HTTPS** in production with proper certificates
3. **Limit exposed ports** using firewall rules
4. **Regular updates** - Pull latest images frequently
5. **Resource limits** - Set memory and CPU limits:

```bash
docker run -p 5001:5001 \
  --memory="512m" \
  --cpus="1.0" \
  trunk8
```

## Next Steps

- Configure [Environment Variables](../configuration/environment.md)
- Set up [Production Deployment](../deployment/production.md)
- Learn about [Backup Strategies](../deployment/backup.md)
- Implement [Security Best Practices](../deployment/security.md) 