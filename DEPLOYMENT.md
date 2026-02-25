# Arni Medica eQMS Deployment Guide

This guide covers deployment of the Arni Medica eQMS Django backend to production and local development environments.

## Quick Start - Local Development with Docker

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for non-Docker development)

### Setup

1. Clone the repository and navigate to the backend directory:
```bash
cd arni-medica-backend
```

2. Create a .env file from the example:
```bash
cp .env.example .env
```

3. Start services with Docker Compose:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Seed initial data:
```bash
docker-compose exec web python manage.py seed_data
```

6. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

7. Access the application:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- Health check: http://localhost:8000/api/health/
- API Docs: http://localhost:8000/api/schema/swagger/

### Docker Services

- **web**: Django development server (port 8000)
- **db**: PostgreSQL 15 database (port 5432)
- **redis**: Redis cache/broker (port 6379)
- **celery**: Celery worker for async tasks
- **celery-beat**: Celery scheduled tasks

### Common Docker Commands

```bash
# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v

# Rebuild after dependency changes
docker-compose build --no-cache

# Run management commands
docker-compose exec web python manage.py <command>
```

## Production Deployment

### Railway.app Deployment

1. **Connect GitHub Repository**
   - Go to Railway.app and create a new project
   - Connect your GitHub repository

2. **Configure Environment Variables**
   - Set required variables in Railway Dashboard:
     ```
     SECRET_KEY=<generate-strong-secret-key>
     DEBUG=False
     ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
     DATABASE_URL=<auto-configured-by-railway>
     REDIS_URL=<auto-configured-by-railway>
     CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
     ```

3. **Deploy**
   - Railway automatically deploys on git push
   - Monitor deployment status in Dashboard
   - Check logs for any issues

4. **Post-Deployment**
   - Run migrations via Railway CLI or SSH
   - Create superuser for admin access
   - Verify health endpoint: `https://yourdomain.com/api/health/`

### Manual Server Deployment (VPS/Self-Hosted)

#### 1. System Setup
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    supervisor

# Create application user
sudo useradd -m -s /bin/bash arni_user
```

#### 2. Database Setup
```bash
# Create PostgreSQL database and user
sudo -u postgres psql << SQL
CREATE DATABASE arni_eqms;
CREATE USER arni_admin WITH PASSWORD 'strong_password_here';
ALTER ROLE arni_admin SET client_encoding TO 'utf8';
ALTER ROLE arni_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE arni_admin SET default_transaction_deferrable TO on;
ALTER ROLE arni_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE arni_eqms TO arni_admin;
\q
SQL
```

#### 3. Application Setup
```bash
# Clone repository
sudo -u arni_user git clone <repo-url> /home/arni_user/arni-medica-backend
cd /home/arni_user/arni-medica-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with production settings
cp .env.example .env
# Edit .env with production values
nano .env
```

#### 4. Django Setup
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Seed initial data
python manage.py seed_data

# Create superuser
python manage.py createsuperuser
```

#### 5. Supervisor Configuration
Create `/etc/supervisor/conf.d/arni-eqms.conf`:
```ini
[program:arni-web]
command=/home/arni_user/arni-medica-backend/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
directory=/home/arni_user/arni-medica-backend
user=arni_user
autostart=true
autorestart=true
stdout_logfile=/var/log/arni-web.log

[program:arni-celery]
command=/home/arni_user/arni-medica-backend/venv/bin/celery -A config worker -l info
directory=/home/arni_user/arni-medica-backend
user=arni_user
autostart=true
autorestart=true
stdout_logfile=/var/log/arni-celery.log

[program:arni-celery-beat]
command=/home/arni_user/arni-medica-backend/venv/bin/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/arni_user/arni-medica-backend
user=arni_user
autostart=true
autorestart=true
stdout_logfile=/var/log/arni-celery-beat.log
```

Start services:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

#### 6. Nginx Configuration
Create `/etc/nginx/sites-available/arni-eqms`:
```nginx
upstream arni_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://arni_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/arni_user/arni-medica-backend/staticfiles/;
    }

    location /media/ {
        alias /home/arni_user/arni-medica-backend/media/;
    }
}
```

Enable site and test:
```bash
sudo ln -s /etc/nginx/sites-available/arni-eqms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. SSL Certificate (Let's Encrypt)
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Monitoring & Maintenance

### Health Checks
- Endpoint: `/api/health/`
- Returns status of application and database
- Use with load balancers and monitoring tools

### Database Backups
```bash
# PostgreSQL backup
pg_dump -U arni_admin arni_eqms > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -U arni_admin arni_eqms < backup_file.sql
```

### Logs
- Django logs: Check Supervisor logs or systemd journal
- Access logs: `/var/log/nginx/access.log`
- Error logs: `/var/log/nginx/error.log`

### Updates & Maintenance
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations after updates
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo supervisorctl restart all
```

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U arni_admin -d arni_eqms -c "SELECT 1"

# Check connection in Django shell
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
```

### Celery Not Processing Tasks
```bash
# Check Celery worker status
sudo supervisorctl status arni-celery

# View Celery logs
sudo tail -f /var/log/arni-celery.log

# Restart Celery
sudo supervisorctl restart arni-celery
```

### Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check file permissions
ls -la staticfiles/

# Restart Nginx
sudo systemctl restart nginx
```

## Performance Optimization

- Ensure database indexes are created on commonly filtered fields
- Use Django Debug Toolbar in development (not in production)
- Configure Redis caching for frequently accessed data
- Use Celery for long-running tasks
- Monitor Gunicorn worker count and adjust based on CPU cores

## Security Checklist

- [ ] Set strong SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS correctly
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags (SECURE_COOKIE_SECURE, etc.)
- [ ] Configure CORS properly
- [ ] Use environment variables for sensitive data
- [ ] Regular database backups
- [ ] Monitor application logs for errors
- [ ] Keep dependencies updated

For compliance documentation (ISO 13485, FDA 21 CFR Part 11, etc.), see COMPLIANCE.md
# Deploy trigger Wed Feb 25 19:49:30 UTC 2026
