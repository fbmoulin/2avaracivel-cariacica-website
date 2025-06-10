# Deployment Guide - 2ª Vara Cível de Cariacica

## Production Deployment Checklist

### Pre-Deployment Requirements

#### Infrastructure
- [ ] Ubuntu 20.04+ or CentOS 8+ server
- [ ] 4+ CPU cores, 8GB+ RAM, 50GB+ SSD
- [ ] PostgreSQL 13+ installed and configured
- [ ] Redis 6.0+ installed (optional but recommended)
- [ ] Nginx 1.18+ installed for reverse proxy
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Domain name configured and DNS pointing to server

#### Security
- [ ] Firewall configured (UFW or iptables)
- [ ] SSH key-based authentication enabled
- [ ] Non-root user created for application
- [ ] Fail2ban installed and configured
- [ ] Security updates applied

### Step-by-Step Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server nginx \
    certbot python3-certbot-nginx ufw fail2ban

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Create application user
sudo useradd -m -s /bin/bash courtapp
sudo usermod -aG sudo courtapp
```

#### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE courtapp_production;
CREATE USER courtapp_user WITH ENCRYPTED PASSWORD 'SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE courtapp_production TO courtapp_user;
ALTER USER courtapp_user CREATEDB;
\q

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
# Uncomment and modify:
# listen_addresses = 'localhost'
# max_connections = 100
# shared_buffers = 256MB
# effective_cache_size = 1GB

sudo systemctl restart postgresql
```

#### 3. Application Deployment

```bash
# Switch to application user
sudo su - courtapp

# Create application directory
mkdir -p /home/courtapp/app
cd /home/courtapp/app

# Clone or upload application files
# (Replace with your actual deployment method)
git clone https://github.com/your-repo/court-website.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production environment file
cat > .env << 'EOF'
FLASK_ENV=production
SECRET_KEY=your_very_long_and_random_secret_key_here
DATABASE_URL=postgresql://courtapp_user:SECURE_PASSWORD_HERE@localhost/courtapp_production
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
WTF_CSRF_ENABLED=True
EOF

# Set proper permissions
chmod 600 .env
```

#### 4. Database Initialization

```bash
# Initialize database tables
python -c "
from app_factory import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Run health check
python debug_log.py
```

#### 5. System Service Configuration

```bash
# Create systemd service file
sudo nano /etc/systemd/system/courtapp.service
```

```ini
[Unit]
Description=2ª Vara Cível de Cariacica Web Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=courtapp
Group=courtapp
WorkingDirectory=/home/courtapp/app
Environment=PATH=/home/courtapp/app/venv/bin
EnvironmentFile=/home/courtapp/app/.env
ExecStart=/home/courtapp/app/venv/bin/gunicorn --bind 127.0.0.1:5000 \
    --workers 4 \
    --worker-class gthread \
    --threads 2 \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --keep-alive 2 \
    --preload \
    --access-logfile /home/courtapp/app/logs/access.log \
    --error-logfile /home/courtapp/app/logs/error.log \
    --capture-output \
    main_optimized:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Create logs directory
mkdir -p /home/courtapp/app/logs

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable courtapp
sudo systemctl start courtapp

# Check status
sudo systemctl status courtapp
```

#### 6. Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/courtapp
```

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;

# Upstream backend
upstream courtapp_backend {
    server 127.0.0.1:5000 fail_timeout=10s max_fails=3;
    keepalive 64;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/css
        text/javascript
        text/xml
        text/plain
        text/x-component
        application/javascript
        application/x-javascript
        application/json
        application/xml
        application/rss+xml
        application/atom+xml
        font/truetype
        font/opentype
        application/vnd.ms-fontobject
        image/svg+xml;

    # Static files
    location /static/ {
        alias /home/courtapp/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Security for static files
        location ~* \.(php|jsp|pl|py|asp|sh|cgi)$ {
            deny all;
        }
    }

    # API endpoints with rate limiting
    location /chatbot/api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://courtapp_backend;
        include /etc/nginx/proxy_params;
    }

    location /admin/ {
        # Restrict admin access to specific IPs
        allow 192.168.1.0/24;  # Internal network
        allow 10.0.0.0/8;      # VPN network
        deny all;
        
        proxy_pass http://courtapp_backend;
        include /etc/nginx/proxy_params;
    }

    # Main application
    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://courtapp_backend;
        include /etc/nginx/proxy_params;
        
        # Proxy timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (no rate limiting)
    location /health {
        proxy_pass http://courtapp_backend;
        include /etc/nginx/proxy_params;
        access_log off;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /404.html {
        root /var/www/html;
    }
    
    location = /50x.html {
        root /var/www/html;
    }
}
```

```bash
# Create proxy parameters file
sudo nano /etc/nginx/proxy_params
```

```nginx
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_redirect off;
proxy_buffering off;
```

```bash
# Enable site and test configuration
sudo ln -s /etc/nginx/sites-available/courtapp /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

#### 7. SSL Certificate Setup

```bash
# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Add renewal to crontab
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 8. Monitoring and Logging Setup

```bash
# Create log rotation configuration
sudo nano /etc/logrotate.d/courtapp
```

```
/home/courtapp/app/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 courtapp courtapp
    postrotate
        systemctl reload courtapp
    endscript
}
```

```bash
# Set up monitoring scripts
mkdir -p /home/courtapp/scripts

cat > /home/courtapp/scripts/health_monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/home/courtapp/app/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check if service is running
if ! systemctl is-active --quiet courtapp; then
    echo "$DATE CRITICAL: courtapp service is down" >> $LOG_FILE
    systemctl start courtapp
    exit 2
fi

# Check HTTP response
if ! curl -f -s http://localhost:5000/health > /dev/null; then
    echo "$DATE WARNING: health endpoint not responding" >> $LOG_FILE
    exit 1
fi

# Check database
if ! su - courtapp -c "cd /home/courtapp/app && python -c 'from app_factory import create_app, db; app=create_app(); app.app_context().push(); db.engine.execute(\"SELECT 1\")'"; then
    echo "$DATE CRITICAL: database connection failed" >> $LOG_FILE
    exit 2
fi

echo "$DATE OK: all checks passed" >> $LOG_FILE
EOF

chmod +x /home/courtapp/scripts/health_monitor.sh

# Add to cron
crontab -e
# Add: */5 * * * * /home/courtapp/scripts/health_monitor.sh
```

### Post-Deployment Verification

#### 1. Functional Testing

```bash
# Test main endpoints
curl -I https://your-domain.com/
curl -I https://your-domain.com/health
curl -I https://your-domain.com/sobre
curl -I https://your-domain.com/servicos/

# Test chatbot API
curl -X POST https://your-domain.com/chatbot/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "teste"}'

# Test rate limiting
for i in {1..35}; do
  curl -s https://your-domain.com/chatbot/api/message \
    -H "Content-Type: application/json" \
    -d '{"message": "teste"}' &
done
```

#### 2. Performance Testing

```bash
# Install testing tools
sudo apt install apache2-utils

# Basic load test
ab -n 100 -c 10 https://your-domain.com/

# More comprehensive test
ab -n 1000 -c 50 -H "Accept-Encoding: gzip" https://your-domain.com/
```

#### 3. Security Verification

```bash
# SSL test
curl -I https://your-domain.com/ | grep -i security

# Header check
curl -I https://your-domain.com/ | grep -E "(X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security)"

# Port scan (should only show 22, 80, 443)
nmap -sS your-domain.com
```

### Backup Strategy

#### Database Backup

```bash
# Create backup script
cat > /home/courtapp/scripts/backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/courtapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U courtapp_user -h localhost courtapp_production | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
EOF

chmod +x /home/courtapp/scripts/backup_database.sh

# Schedule daily backup
crontab -e
# Add: 0 2 * * * /home/courtapp/scripts/backup_database.sh
```

#### Application Backup

```bash
# Create application backup script
cat > /home/courtapp/scripts/backup_application.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/courtapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Application files backup (excluding logs and cache)
tar --exclude='logs' --exclude='__pycache__' --exclude='.git' \
    -czf $BACKUP_DIR/app_$DATE.tar.gz -C /home/courtapp app

# Keep only last 7 days
find $BACKUP_DIR -name "app_*.tar.gz" -mtime +7 -delete

echo "Application backup completed: $BACKUP_DIR/app_$DATE.tar.gz"
EOF

chmod +x /home/courtapp/scripts/backup_application.sh

# Schedule weekly backup
crontab -e
# Add: 0 3 * * 0 /home/courtapp/scripts/backup_application.sh
```

### Maintenance Procedures

#### Regular Updates

```bash
# Create update script
cat > /home/courtapp/scripts/update_system.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting system update..."

# Backup before update
/home/courtapp/scripts/backup_application.sh
/home/courtapp/scripts/backup_database.sh

# Update system packages
sudo apt update
sudo apt upgrade -y

# Update Python packages
cd /home/courtapp/app
source venv/bin/activate
pip list --outdated
# pip install --upgrade package_name  # Manual review required

# Restart services
sudo systemctl restart courtapp
sudo systemctl reload nginx

# Health check
sleep 10
curl -f http://localhost:5000/health

echo "Update completed successfully"
EOF

chmod +x /home/courtapp/scripts/update_system.sh
```

#### Log Cleanup

```bash
# Automatic log cleanup
cat > /home/courtapp/scripts/cleanup_logs.sh << 'EOF'
#!/bin/bash
LOG_DIR="/home/courtapp/app/logs"

# Remove logs older than 30 days
find $LOG_DIR -name "*.log.*" -mtime +30 -delete

# Compress large current logs
find $LOG_DIR -name "*.log" -size +100M -exec gzip {} \;

echo "Log cleanup completed"
EOF

chmod +x /home/courtapp/scripts/cleanup_logs.sh

# Schedule weekly cleanup
crontab -e
# Add: 0 1 * * 0 /home/courtapp/scripts/cleanup_logs.sh
```

### Troubleshooting Common Issues

#### Application Won't Start

```bash
# Check service status
sudo systemctl status courtapp

# Check logs
sudo journalctl -u courtapp -f

# Check application logs
tail -f /home/courtapp/app/logs/error.log

# Check permissions
ls -la /home/courtapp/app/
ls -la /home/courtapp/app/.env
```

#### Database Connection Issues

```bash
# Test database connection
sudo -u postgres psql -c "\l"

# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection as application user
su - courtapp -c "cd /home/courtapp/app && python -c 'from app_factory import create_app, db; app=create_app(); app.app_context().push(); print(db.engine.execute(\"SELECT version()\").scalar())'"
```

#### High Memory Usage

```bash
# Check memory usage
free -h
ps aux | grep gunicorn | head -10

# Restart application
sudo systemctl restart courtapp

# Monitor memory
watch -n 5 free -h
```

#### SSL Certificate Issues

```bash
# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout | grep "Not After"

# Renew certificate
sudo certbot renew

# Test SSL configuration
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### Security Hardening

#### Additional Security Measures

```bash
# Install and configure fail2ban
sudo apt install fail2ban

sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

This deployment guide provides a comprehensive approach to setting up the court website in a production environment with proper security, monitoring, and maintenance procedures.