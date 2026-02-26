# Batch Records App - Installation & Setup Guide

## Quick Start

### 1. Add to Django Settings

```python
# settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'django_filters',

    # Your apps
    'core',
    'documents',
    'users',
    'equipment',
    'deviations',
    'capa',

    # NEW: Batch Records app
    'batch_records',
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 2. Include URLs

```python
# urls.py (main project)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/batch_records/', include('batch_records.urls')),
    # ... other patterns
]
```

### 3. Run Migrations

```bash
# Create migration files
python manage.py makemigrations batch_records

# Apply migrations
python manage.py migrate batch_records
```

### 4. Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 5. Test the Installation

```bash
# Run tests
python manage.py test batch_records

# Start development server
python manage.py runserver

# Access admin interface
# http://localhost:8000/admin/

# Try API endpoint (with token)
# http://localhost:8000/api/batch_records/batch-records/
```

## Dependency Requirements

### Required Django Packages

```bash
pip install django>=3.2
pip install djangorestframework>=3.12
pip install django-filter>=2.4
```

### Requirements.txt Entry

```txt
Django>=3.2,<5.0
djangorestframework>=3.12
django-filter>=2.4
```

## Database Requirements

### Depends on Following Models

The app expects these models to exist in your project:

1. **core.models.AuditedModel**
   - All models inherit from this
   - Must have: created_by, updated_by, created_at, updated_at fields
   - Must have: save() method handling for created_by/updated_by

2. **documents.Document** (optional FK)
   - Referenced by: MasterBatchRecord.linked_document

3. **users.ProductLine** (optional FK)
   - Referenced by: MasterBatchRecord.product_line

4. **users.Site** (optional FK)
   - Referenced by: BatchRecord.site

5. **equipment.Equipment** (optional FK)
   - Referenced by: BatchEquipment.equipment

6. **deviations.Deviation** (optional FK)
   - Referenced by: BatchDeviation.linked_deviation

7. **capa.CAPA** (optional FK)
   - Referenced by: BatchDeviation.linked_capa

8. **django.contrib.auth.User** (built-in)
   - Referenced throughout for approvals and signatures

## Production Deployment Checklist

- [ ] Set DEBUG = False in production settings
- [ ] Configure allowed HOSTS
- [ ] Use secure database backend (PostgreSQL recommended)
- [ ] Enable HTTPS/SSL
- [ ] Configure proper SECRET_KEY
- [ ] Run migrations on production database
- [ ] Create production superuser
- [ ] Configure static files collection
- [ ] Set up proper logging
- [ ] Configure email backend
- [ ] Enable CSRF protection
- [ ] Set up monitoring/alerts
- [ ] Configure backup strategy
- [ ] Review CORS settings if needed
- [ ] Test API endpoints with production URLs

## Admin Interface Setup

Access the admin interface at `/admin/`:

1. **Master Batch Records**
   - View/Create/Edit/Delete
   - Approve records
   - Filter by status, product line
   - Search by ID, title, product code

2. **Batch Records**
   - View/Create/Edit/Delete
   - Monitor status transitions
   - View associated steps, materials, equipment
   - Filter by status, site, deviations
   - Search by batch ID, number, lot number

3. **Batch Steps**
   - View/Create/Edit/Delete
   - See operator and verifier signatures
   - Monitor completion status
   - View collected data

4. **Batch Deviations**
   - View/Create/Edit/Delete
   - Monitor resolution status
   - Link to CAPA items
   - Filter by type and status

5. **Batch Materials**
   - View/Create/Edit/Delete
   - Track dispensing and consumption
   - View lot numbers
   - Monitor material status

6. **Batch Equipment**
   - View/Create/Edit/Delete
   - Track calibration and cleaning
   - Monitor usage times
   - View verification status

## API Configuration

### Authentication

The app uses Django REST Framework's Token Authentication. Generate tokens:

```python
# In Django shell or management command
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='username')
token, created = Token.objects.get_or_create(user=user)
print(token.key)
```

Use token in headers:
```
Authorization: Token <token_key>
```

### CORS Configuration (if needed)

```python
# settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

### Pagination Configuration

```python
# settings.py
REST_FRAMEWORK = {
    ...
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## Database Schema

The app creates the following database tables:

```
batch_records_masterbatchrecord
batch_records_batchrecord
batch_records_batchstep
batch_records_batchdeviation
batch_records_batchmaterial
batch_records_batchequipment
```

### Indexes Created

- mbr_id (unique)
- batch_id (unique)
- batch_number (unique)
- deviation_id (unique)
- product_code
- status
- (batch, step_number) - composite unique
- (batch, status)
- Foreign key indexes

## Signals

The app automatically registers signal handlers for:

1. **BatchDeviation save/delete**
   - Updates parent batch's `has_deviations` flag
   - Triggered automatically via signals.py

## Testing

Run the test suite:

```bash
# All tests
python manage.py test batch_records

# Specific test class
python manage.py test batch_records.tests.MasterBatchRecordTestCase

# Specific test method
python manage.py test batch_records.tests.MasterBatchRecordTestCase.test_mbr_creation

# With verbose output
python manage.py test batch_records -v 2

# Coverage report (requires coverage package)
coverage run --source='batch_records' manage.py test batch_records
coverage report
coverage html
```

## Development Setup

### Local Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file for development settings
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver

# In another terminal, access:
# Admin: http://localhost:8000/admin/
# API: http://localhost:8000/api/batch_records/
```

### IDE Setup

**PyCharm:**
1. File → Settings → Project → Python Interpreter → Add → Existing Environment
2. Select venv/bin/python
3. Mark batch_records as Sources Root
4. Enable Django support: Settings → Languages & Frameworks → Django

**VS Code:**
1. Install Python extension
2. Select Python interpreter from venv
3. Create .vscode/settings.json:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.defaultFormatter": "ms-python.python",
        "editor.formatOnSave": true
    }
}
```

## Troubleshooting

### Migration Errors

```bash
# If migrations fail, check model state
python manage.py makemigrations --dry-run

# Reset migrations (dev only)
python manage.py migrate batch_records zero
python manage.py migrate batch_records

# Show migration plan
python manage.py showmigrations batch_records
```

### Missing Related Models

If you get ForeignKey errors:
```
django.core.exceptions.ImproperlyConfigured:
Field batch_records.MasterBatchRecord.product_line has a relation to model
users.ProductLine that hasn't been installed
```

Solution: Ensure all referenced apps are in INSTALLED_APPS before batch_records:
```python
INSTALLED_APPS = [
    ...
    'documents',
    'users',
    'equipment',
    'deviations',
    'capa',
    'batch_records',  # After dependencies
]
```

### Permission Denied Errors

Ensure user has permission to access:
```python
# Grant staff/superuser status
user.is_staff = True
user.is_superuser = True
user.save()

# Or create specific permissions
from django.contrib.auth.models import Permission
from batch_records.models import BatchRecord

perm = Permission.objects.get(codename='change_batchrecord')
user.user_permissions.add(perm)
```

### API Token Issues

```bash
# Regenerate token for user
python manage.py shell
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
token = Token.objects.get(user=user)
token.delete()
token = Token.objects.create(user=user)
print(token.key)
```

## Performance Optimization

### Database Optimization

```python
# Use select_related for foreign keys
queryset = BatchRecord.objects.select_related('mbr', 'site', 'released_by')

# Use prefetch_related for reverse relations
queryset = BatchRecord.objects.prefetch_related('steps', 'deviations', 'materials')

# Combine for nested queries
queryset = (BatchRecord.objects
    .select_related('mbr', 'site')
    .prefetch_related('steps', 'deviations'))
```

### Caching

```python
# Add caching to settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache queries
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def batch_list(request):
    ...
```

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump -U username -h localhost database_name > backup.sql

# MySQL
mysqldump -u username -p database_name > backup.sql
```

### Data Export

```bash
# Export batch records to JSON
python manage.py dumpdata batch_records > batch_records_backup.json

# Restore from JSON
python manage.py loaddata batch_records_backup.json
```

## Monitoring & Logging

### Django Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/batch_records.log',
        },
    },
    'loggers': {
        'batch_records': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Monitoring Query Performance

```python
# Enable query logging in development
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

## Documentation

- **README.md** - Complete app documentation
- **EXAMPLES.md** - API usage examples
- **STRUCTURE.txt** - App structure overview
- **INSTALLATION.md** - This file
