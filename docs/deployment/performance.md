# Performance Optimization

This comprehensive guide covers performance optimization strategies for Trunk8 in production environments, including application tuning, infrastructure optimization, and monitoring best practices.

## Performance Overview

Key performance areas for Trunk8:

- **Response time** - How quickly requests are served
- **Throughput** - Number of requests handled per second
- **Resource utilization** - CPU, memory, disk, and network usage
- **Scalability** - Ability to handle increased load
- **Availability** - System uptime and reliability

## Performance Metrics to Monitor

### Application Metrics

- **Response Time**
    - Average: < 200ms for page loads
    - 95th percentile: < 500ms
    - 99th percentile: < 1000ms

- **Throughput**
    - Links served: Target 1000+ requests/second
    - File downloads: Based on bandwidth capacity
    - Admin operations: 50+ requests/second

- **Error Rates**
    - Target: < 0.1% error rate
    - Monitor 4xx and 5xx responses

### System Metrics

- **CPU Usage**: Target < 70% average
- **Memory Usage**: Target < 80% of available RAM
- **Disk I/O**: Monitor read/write operations
- **Network**: Bandwidth utilization and latency

## Application-Level Optimization

### 1. Gunicorn Configuration

#### Worker Process Optimization

```bash
# Calculate optimal worker count
workers = (2 × CPU_cores) + 1

# For a 4-core system
workers = 9
```

**Production Gunicorn Configuration:**

```bash
# /etc/systemd/system/trunk8.service
[Unit]
Description=Trunk8 Application
After=network.target

[Service]
User=trunk8
Group=trunk8
WorkingDirectory=/opt/trunk8
Environment=PATH=/opt/trunk8/.venv/bin
Environment=TRUNK8_ADMIN_PASSWORD=your-secure-password
Environment=TRUNK8_SECRET_KEY=your-secret-key
ExecStart=/opt/trunk8/.venv/bin/gunicorn \
    --workers 9 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --bind unix:/opt/trunk8/trunk8.sock \
    --access-logfile /var/log/trunk8/access.log \
    --error-logfile /var/log/trunk8/error.log \
    --log-level info \
    run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Worker Class Selection

```bash
# Sync workers (default) - good for CPU-bound tasks
--worker-class sync

# Async workers - for I/O bound tasks (future enhancement)
--worker-class gevent --worker-connections 1000

# Threaded workers - for mixed workloads
--worker-class gthread --threads 2-4
```

### 2. Configuration Caching Optimization

The configuration loader already implements caching, but can be tuned:

```python
# In app/utils/config_loader.py - optimization suggestions

class ConfigLoader:
    def __init__(self):
        self._cache_ttl = 300  # 5 minute cache TTL
        self._force_reload_interval = 3600  # Force reload every hour
```

### 3. Session Optimization

```toml
# config/config.toml
[session]
permanent_lifetime_days = 7  # Shorter sessions reduce memory usage
```

### 4. File Serving Optimization

**Let web server handle static files:**

```nginx
# In nginx configuration
location /static {
    alias /opt/trunk8/app/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip_static on;
}

# User assets (requires careful consideration for security)
location ~ ^/([a-zA-Z0-9_-]+)/assets/ {
    internal;  # Only accessible via X-Accel-Redirect
    alias /opt/trunk8/users/$1/assets/;
}
```

## Web Server Optimization

### Nginx Performance Tuning

#### Basic Configuration

```nginx
# /etc/nginx/nginx.conf

user www-data;
worker_processes auto;  # Use all available CPU cores
worker_rlimit_nofile 65535;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    # Basic optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 50m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;
}
```

#### Trunk8-Specific Configuration

```nginx
# /etc/nginx/sites-available/trunk8

upstream trunk8_backend {
    server unix:/opt/trunk8/trunk8.sock;
    
    # For multiple workers/servers
    # server 127.0.0.1:5001 weight=3;
    # server 127.0.0.1:5002 weight=2;
    
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name trunk8.example.com;
    
    # SSL configuration (optimized)
    ssl_certificate /etc/letsencrypt/live/trunk8.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trunk8.example.com/privkey.pem;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # Performance headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Static file serving with caching
    location /static/ {
        alias /opt/trunk8/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    
    location /auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://trunk8_backend;
        include proxy_params;
    }
    
    location / {
        limit_req zone=general burst=20 nodelay;
        
        # Proxy configuration
        proxy_pass http://trunk8_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
}
```

### Caching Strategies

#### Browser Caching

```nginx
# Static assets
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# HTML pages (short cache for dynamic content)
location ~* \.(html)$ {
    expires 5m;
    add_header Cache-Control "public, must-revalidate";
}
```

#### Nginx Proxy Caching

```nginx
# In http block
proxy_cache_path /var/cache/nginx/trunk8 levels=1:2 keys_zone=trunk8:10m max_size=1g inactive=60m;

# In server block
location / {
    proxy_cache trunk8;
    proxy_cache_valid 200 5m;
    proxy_cache_valid 404 1m;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    proxy_cache_lock on;
    
    # Cache bypass for admin operations
    proxy_cache_bypass $cookie_sessionid;
    proxy_no_cache $cookie_sessionid;
    
    proxy_pass http://trunk8_backend;
}
```

## Infrastructure Optimization

### 1. Vertical Scaling

#### CPU Optimization

```bash
# Check CPU usage
htop
vmstat 1

# CPU-bound optimization
echo 'performance' > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

#### Memory Optimization

```bash
# Check memory usage
free -h
cat /proc/meminfo

# Optimize swap (if needed)
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# Optimize file system cache
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
```

#### Storage Optimization

```bash
# Use SSD storage for better I/O performance
# Mount with optimized options
/dev/sda1 /opt/trunk8 ext4 noatime,data=writeback 0 1

# Monitor disk I/O
iotop
iostat -x 1
```

### 2. Horizontal Scaling

#### Load Balancer Configuration

```nginx
# /etc/nginx/nginx.conf
upstream trunk8_cluster {
    least_conn;  # Load balancing method
    
    server 10.0.1.10:5001 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:5001 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:5001 weight=2 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

server {
    location / {
        proxy_pass http://trunk8_cluster;
        # ... proxy settings
    }
}
```

#### Shared Storage Setup

```bash
# NFS for shared assets
# On NFS server
sudo apt install nfs-kernel-server
echo '/srv/trunk8-assets 10.0.1.0/24(rw,sync,no_subtree_check)' >> /etc/exports
exportfs -ra

# On application servers
sudo apt install nfs-common
mount -t nfs nfs-server:/srv/trunk8-assets /opt/trunk8/users
```

### 3. Database Preparation (Future)

When database support is added:

```postgresql
-- PostgreSQL optimization
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1  # For SSD storage

-- Connection pooling with PgBouncer
[databases]
trunk8 = host=localhost port=5432 dbname=trunk8

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 50
```

## Monitoring and Alerting

### 1. Application Monitoring

#### Prometheus + Grafana Setup

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

#### Flask Metrics Integration

```python
# Add to requirements.txt
# prometheus-flask-exporter

# In app/__init__.py
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    app = Flask(__name__)
    
    # Initialize metrics
    metrics = PrometheusMetrics(app)
    
    # Custom metrics
    metrics.info('trunk8_info', 'Application info', version='1.0')
    
    return app
```

### 2. System Monitoring

#### Node Exporter for System Metrics

```bash
# Install node_exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.3.1.linux-amd64.tar.gz
sudo cp node_exporter-1.3.1.linux-amd64/node_exporter /usr/local/bin/

# Systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now node_exporter
```

### 3. Log Analysis

#### Centralized Logging

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
      
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

### 4. Performance Dashboards

#### Key Performance Indicators

```python
# Custom metrics to track
request_duration = Histogram('request_duration_seconds', 'Request duration')
request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
active_users = Gauge('active_users', 'Number of active users')
link_access_rate = Counter('link_accesses_total', 'Total link accesses')
file_download_size = Histogram('file_download_bytes', 'File download sizes')
```

## Common Performance Bottlenecks

### 1. File I/O Operations

**Problem**: Slow file uploads/downloads
**Solutions**:

- Use SSD storage
- Add file size limits
- Use CDN for large files

### 2. Configuration Reloading

**Problem**: Frequent TOML file parsing

**Solutions**:

- Already optimized with modification time checking
- Implement configuration change notifications

### 3. Session Management

**Problem**: High memory usage from sessions

**Solutions**:

- Shorter session timeouts
- Session cleanup jobs


## Performance Testing

### 1. Load Testing with Apache Bench

```bash
# Test concurrent requests
ab -n 1000 -c 50 http://trunk8.example.com/

# Test with authentication
ab -n 1000 -c 50 -C "sessionid=your-session-id" http://trunk8.example.com/links

# Test file downloads
ab -n 100 -c 10 http://trunk8.example.com/your-file-link
```

### 2. Load Testing with wrk

```bash
# Install wrk
sudo apt install wrk

# Basic load test
wrk -t12 -c400 -d30s http://trunk8.example.com/

# POST request test
wrk -t12 -c400 -d30s -s post.lua http://trunk8.example.com/add
```

### 3. Stress Testing

```bash
# Test resource limits
stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 60s

# Monitor during stress test
htop
iotop
nethogs
```

## Performance Optimization Checklist

### Application Level
- [ ] Optimize Gunicorn worker count
- [ ] Configure appropriate worker class
- [ ] Add response caching where appropriate
- [ ] Optimize session settings

### Web Server Level
- [ ] Configure Nginx optimization settings
- [ ] Enable gzip compression
- [ ] Set up proper caching headers
- [ ] Implement rate limiting
- [ ] Use HTTP/2

### Infrastructure Level
- [ ] Use SSD storage
- [ ] Optimize file system mount options
- [ ] Configure kernel parameters
- [ ] Set up monitoring and alerting
- [ ] Plan for horizontal scaling

## Best Practices

### Development
- Profile code to identify bottlenecks
- Use async operations for I/O bound tasks
- Implement proper error handling
- Add performance logging

### Deployment
- Use staging environment for performance testing
- Implement gradual rollouts
- Monitor key metrics continuously
- Set up automated alerts

### Maintenance
- Regular performance reviews
- Update dependencies for security and performance
- Clean up old data (expired links, logs)
- Review and optimize configurations

## Next Steps

- Implement [Production Deployment](production.md) with performance considerations
- Set up [Security Monitoring](security.md) alongside performance monitoring
- Configure [System Backups](backup.md) that don't impact performance
- Review application architecture for scaling opportunities 