# Validation Management App - Deployment Guide

## Pre-Deployment Checklist

### Environment Setup

- [ ] Python 3.8+ installed
- [ ] Django 3.2+ installed
- [ ] Django REST Framework installed
- [ ] django-filter installed
- [ ] Virtual environment activated

```bash
pip install Django djangorestframework django-filter
```

### Project Configuration

- [ ] Add `validation_mgmt` to INSTALLED_APPS
- [ ] Configure REST_FRAMEWORK settings
- [ ] Add validation_mgmt URLs to main urls.py
- [ ] Configure MEDIA_ROOT and MEDIA_URL for file uploads
- [ ] Database configured (PostgreSQL recommended for production)

### Settings.py Configuration

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'django_filters',

    # Project apps
    'core',
    'users',
    'documents',
    'deviations',
    'validation_mgmt',  # Add this
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# For file uploads
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

### URLs Configuration

Add to main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/validation/', include('validation_mgmt.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Database Migration Steps

### 1. Create Migrations

```bash
python manage.py makemigrations validation_mgmt
```

Expected output:
```
Migrations for 'validation_mgmt':
  validation_mgmt/migrations/0001_initial.py
    - Create model ValidationPlan
    - Create model ValidationProtocol
    - Create model ValidationTestCase
    - Create model RTMEntry
    - Create model ValidationDeviation
    - Create model ValidationSummaryReport
```

### 2. Review Migrations

```bash
python manage.py sqlmigrate validation_mgmt 0001
```

This shows the SQL that will be executed.

### 3. Apply Migrations

```bash
python manage.py migrate validation_mgmt
```

Expected output:
```
Operations to perform:
  Apply all migrations: validation_mgmt
Running migrations:
  Applying validation_mgmt.0001_initial... OK
```

### 4. Verify Database

```bash
python manage.py dbshell
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'validation%';
```

Should return 6 tables:
- validation_mgmt_validationplan
- validation_mgmt_validationprotocol
- validation_mgmt_validationtestcase
- validation_mgmt_rtmentry
- validation_mgmt_validationdeviation
- validation_mgmt_validationsummaryreport

---

## Development Deployment

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure requirements.txt includes:
```
Django>=3.2
djangorestframework>=3.12
django-filter>=21.1
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

### 3. Run Development Server

```bash
python manage.py runserver
```

Access at:
- API: http://localhost:8000/api/validation/
- Admin: http://localhost:8000/admin/

### 4. Test Basic Functionality

```bash
# Test API access
curl http://localhost:8000/api/validation/validation-plans/

# Test admin
# Navigate to http://localhost:8000/admin/
```

---

## Production Deployment

### 1. Security Checklist

```python
# settings.py

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')  # Use environment variable
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/validation_mgmt.log',
        },
    },
    'loggers': {
        'validation_mgmt': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 2. Run Security Checks

```bash
python manage.py check --deploy
```

Expected output:
```
System check identified some issues:

WARNINGS:
W002: You have not set a value for the SECURE_HSTS_SECONDS setting...
...

5 errors found.
```

Fix all errors before deployment.

### 3. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Run Tests

```bash
python manage.py test validation_mgmt --verbosity=2
```

### 5. Database Backup

Before production deployment:

```bash
# PostgreSQL
pg_dump dbname > backup.sql

# MySQL
mysqldump -u user -p dbname > backup.sql
```

### 6. Deploy with Gunicorn

Create `wsgi.py` configuration:

```bash
pip install gunicorn
gunicorn arni_medica_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 7. Deploy with Nginx

Create `/etc/nginx/sites-available/validation`:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    client_max_body_size 5M;

    location /static/ {
        alias /var/www/static/;
    }

    location /media/ {
        alias /var/www/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/validation /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 8. Setup Systemd Service

Create `/etc/systemd/system/django-validation.service`:

```ini
[Unit]
Description=Django Validation Management Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/arni-medica-backend
Environment="PATH=/var/www/venv/bin"
ExecStart=/var/www/venv/bin/gunicorn arni_medica_backend.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable django-validation
systemctl start django-validation
systemctl status django-validation
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "arni_medica_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: arni_medica
      POSTGRES_USER: dbuser
      POSTGRES_PASSWORD: dbpass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn arni_medica_backend.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      DEBUG: 'False'
      SECRET_KEY: 'your-secret-key'
      DB_NAME: arni_medica
      DB_USER: dbuser
      DB_PASSWORD: dbpass
      DB_HOST: db
    depends_on:
      - db
    volumes:
      - ./media:/app/media

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./media:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
```

Deploy:
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## Post-Deployment Verification

### 1. Check API Health

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://yourdomain.com/api/validation/validation-plans/
```

### 2. Verify Admin Access

Navigate to: `http://yourdomain.com/admin/`

### 3. Test File Uploads

Create a protocol with a file and verify it's accessible.

### 4. Monitor Logs

```bash
tail -f /var/log/django/validation_mgmt.log
```

### 5. Database Integrity

```bash
python manage.py check --deploy
python manage.py test validation_mgmt
```

---

## Backup & Recovery

### Automated Daily Backup

Create `/usr/local/bin/backup-validation.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/validation_mgmt"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump arni_medica > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/media/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
0 2 * * * /usr/local/bin/backup-validation.sh >> /var/log/backup-validation.log 2>&1
```

### Recovery from Backup

```bash
# Restore database
psql arni_medica < /backups/validation_mgmt/db_20240115_020000.sql

# Restore media files
tar -xzf /backups/validation_mgmt/media_20240115_020000.tar.gz -C /

# Restart service
systemctl restart django-validation
```

---

## Monitoring & Maintenance

### Application Monitoring

```bash
# Check service status
systemctl status django-validation

# View recent logs
journalctl -u django-validation -n 50

# Monitor resource usage
top -p $(pidof gunicorn)
```

### Database Maintenance

```bash
# PostgreSQL: Analyze and vacuum
python manage.py dbshell
VACUUM ANALYZE;
\q

# Check database size
SELECT pg_size_pretty(pg_database_size('arni_medica'));
```

### Performance Optimization

```python
# settings.py - Enable caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## Troubleshooting

### Issue: 500 Server Error

Check logs:
```bash
tail -f /var/log/django/validation_mgmt.log
systemctl status django-validation
```

### Issue: Database Connection Error

Verify connection:
```bash
python manage.py dbshell
```

### Issue: Static Files Not Loading

Collect static files:
```bash
python manage.py collectstatic --noinput
systemctl restart nginx
```

### Issue: File Upload Fails

Check permissions:
```bash
ls -la /var/www/media/
chmod 755 /var/www/media/
chown www-data:www-data /var/www/media/
```

---

## Rollback Procedure

If deployment has critical issues:

1. **Stop Services**
   ```bash
   systemctl stop django-validation
   systemctl stop nginx
   ```

2. **Restore Previous Database**
   ```bash
   psql arni_medica < /backups/validation_mgmt/db_previous.sql
   ```

3. **Restore Previous Code**
   ```bash
   git checkout previous-stable-version
   ```

4. **Run Migrations if Needed**
   ```bash
   python manage.py migrate
   ```

5. **Restart Services**
   ```bash
   systemctl start django-validation
   systemctl start nginx
   ```

---

## Version Updates

### Update Steps

1. **Backup Database and Media**
   ```bash
   pg_dump arni_medica > backup_pre_update.sql
   tar -czf media_pre_update.tar.gz /var/www/media/
   ```

2. **Update Code**
   ```bash
   git pull origin main
   ```

3. **Install New Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Test**
   ```bash
   python manage.py test validation_mgmt
   ```

7. **Restart Services**
   ```bash
   systemctl restart django-validation
   systemctl restart nginx
   ```

---

## Performance Benchmarks

### Expected Performance

- **List Endpoints:** < 200ms (20 items)
- **Detail Endpoints:** < 100ms
- **Create Endpoint:** < 500ms
- **Filter Queries:** < 300ms
- **Summary Queries:** < 500ms

### Load Testing

Use Apache Bench or similar:
```bash
ab -n 1000 -c 10 -H "Authorization: Token xyz" \
  http://localhost/api/validation/validation-plans/
```

---

## Support Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Nginx: https://nginx.org/en/docs/
- Gunicorn: https://docs.gunicorn.org/

---

## Compliance & Auditing

### 21 CFR Part 11 Compliance

- [ ] Validate user access controls
- [ ] Enable audit logging for all changes
- [ ] Implement digital signatures (if applicable)
- [ ] Archive validation records
- [ ] Document system configuration
- [ ] Maintain change log

### Data Security

- [ ] Enable database encryption
- [ ] Use HTTPS/SSL for all communications
- [ ] Implement role-based access control
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Monitor for vulnerabilities

---

## Conclusion

Follow this guide to deploy the Validation Management app to production successfully. Refer to troubleshooting section for common issues, and maintain regular backups for disaster recovery.

For additional support, consult the technical documentation in IMPLEMENTATION.md and API_ENDPOINTS.md.
