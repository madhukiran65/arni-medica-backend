# Design Controls App - Deployment Guide

## Quick Start (5 Minutes)

### 1. Update Django Settings

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'django_filters',
    
    'core',
    'users',
    'documents',
    'design_controls',  # ADD THIS
]
```

### 2. Update URLs

```python
# urls.py

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/design-controls/', include('design_controls.urls')),  # ADD THIS
    # ... other paths
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations design_controls
python manage.py migrate design_controls
```

### 4. Start Using

```bash
python manage.py runserver
# Visit: http://localhost:8000/admin/design_controls/
# API: http://localhost:8000/api/design-controls/
```

## Production Deployment

### Pre-Deployment Checklist

```bash
# Check for issues
python manage.py check

# Run tests
python manage.py test design_controls

# Collect static files
python manage.py collectstatic --noinput

# Check migrations
python manage.py showmigrations design_controls
```

### Environment Variables

Create a `.env` file:

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=api.example.com,www.example.com
DATABASE_URL=postgresql://user:password@localhost/dbname
MEDIA_ROOT=/var/www/media
MEDIA_URL=/media/
```

### Database Setup

#### PostgreSQL (Recommended)

```bash
# Create database
createdb arni_medica

# Run migrations
python manage.py migrate design_controls
```

#### SQLite (Development Only)

Default Django configuration works with SQLite.

### File Uploads

Configure in settings.py:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media'

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
```

### Gunicorn Setup

```bash
# Install
pip install gunicorn

# Run
gunicorn arni_medica.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --access-logfile - \
  --error-logfile -
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.example.com;

    location /static/ {
        alias /var/www/static/;
    }

    location /media/ {
        alias /var/www/media/;
    }

    location /api/design-controls/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### SSL/HTTPS

```bash
# Use Let's Encrypt with Certbot
sudo certbot certonly --standalone -d api.example.com

# Update Nginx to use SSL
```

## Monitoring & Maintenance

### Application Logging

Configure in settings.py:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/design_controls.log',
        },
    },
    'loggers': {
        'design_controls': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Database Backups

```bash
# PostgreSQL backup
pg_dump arni_medica > backup_$(date +%Y%m%d).sql

# Automated backup (cron job)
0 2 * * * pg_dump arni_medica > /backups/db_$(date +\%Y\%m\%d).sql
```

### Monitoring

Use tools like:
- Sentry for error tracking
- New Relic for performance monitoring
- Prometheus for metrics
- ELK Stack for logs

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "arni_medica.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: arni_medica
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/arni_medica
    depends_on:
      - db

volumes:
  postgres_data:
```

Run with:

```bash
docker-compose up
```

## Cloud Deployment

### AWS Deployment

1. Use Elastic Beanstalk or EC2
2. RDS for database
3. S3 for media files
4. CloudFront for CDN

### Azure Deployment

1. App Service
2. Azure Database for PostgreSQL
3. Azure Storage for media
4. Application Insights for monitoring

### Google Cloud Deployment

1. Cloud Run or Compute Engine
2. Cloud SQL
3. Cloud Storage
4. Cloud Trace for monitoring

## Testing in Production

```bash
# Test API endpoint
curl -X GET http://api.example.com/api/design-controls/design-projects/ \
  -H "Authorization: Token YOUR_TOKEN"

# Create test object
curl -X POST http://api.example.com/api/design-controls/design-projects/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Project",
    "product_type": "device",
    "regulatory_pathway": "510k",
    "project_lead": 1
  }'
```

## Troubleshooting

### Migration Issues

```bash
# Show migration status
python manage.py showmigrations design_controls

# Reset migrations (DANGEROUS - development only!)
python manage.py migrate design_controls zero
python manage.py migrate design_controls
```

### Import Errors

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Permissions Issues

Check file and directory permissions:

```bash
sudo chown -R www-data:www-data /var/www/media
sudo chmod -R 755 /var/www/media
```

### Database Connection Issues

Test connection:

```bash
python manage.py dbshell
```

## Scaling Considerations

### For Small Deployments (< 10k users)
- Single server
- SQLite or PostgreSQL
- File storage on local filesystem

### For Medium Deployments (10k - 100k users)
- Application servers with load balancer
- PostgreSQL with replication
- S3 for file storage
- Redis for caching

### For Large Deployments (> 100k users)
- Multi-region deployment
- Database sharding
- CDN for static files
- Message queue (Celery)
- Distributed caching

## Maintenance

### Weekly Tasks
- Monitor logs
- Check disk usage
- Review performance metrics

### Monthly Tasks
- Update dependencies
- Review security updates
- Backup verification

### Quarterly Tasks
- Full system audit
- Capacity planning
- Security penetration test

## Support & Documentation

See for detailed information:
- `README.md` - API Reference
- `EXAMPLES.md` - Usage Examples
- `INTEGRATION.md` - Setup Details
- `CHECKLIST.md` - Implementation Checklist

## Emergency Procedures

### Database Corruption

```bash
# Restore from backup
psql arni_medica < backup.sql

# Verify restoration
python manage.py check
```

### Memory Leak

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Check memory usage
free -h
```

### API Down

```bash
# Check status
systemctl status gunicorn

# View logs
tail -f /var/log/django/design_controls.log

# Restart
systemctl restart gunicorn
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_design_project_status ON design_controls_designproject(status);
CREATE INDEX idx_user_need_project ON design_controls_userneed(project_id);
CREATE INDEX idx_vv_protocol_result ON design_controls_vvprotocol(result);
```

### API Caching

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Query Optimization

Use `select_related()` and `prefetch_related()` for M2M:

```python
DesignProject.objects.select_related('project_lead').prefetch_related('user_needs')
```

## Conclusion

The Design Controls app is now deployed and ready for production use.

For ongoing support and updates:
- Review logs regularly
- Monitor performance
- Plan for scaling
- Keep documentation updated
- Test disaster recovery procedures
