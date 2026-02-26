# Design Controls App - Integration Guide

## Quick Start

### Step 1: Update Django Settings

Add `design_controls` to your `INSTALLED_APPS`:

```python
# settings.py or settings/base.py

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
    'corsheaders',

    # Local apps
    'core',
    'users',
    'documents',
    'design_controls',  # ADD THIS LINE
]
```

Ensure REST Framework is configured:

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Step 2: Update Main URLs

Include the design_controls URLs in your main `urls.py`:

```python
# urls.py or urls.py/api.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_rest_framework_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include_rest_framework_urls),

    # API endpoints
    path('api/design-controls/', include('design_controls.urls')),
    path('api/users/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    # ... other app URLs
]
```

### Step 3: Run Migrations

```bash
# Create migrations
python manage.py makemigrations design_controls

# Apply migrations
python manage.py migrate design_controls

# Or in one step
python manage.py migrate
```

### Step 4: Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### Step 5: Access Admin Interface

Start your development server:

```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin/` and log in. You should see:

- Design Controls
  - Design Projects
  - User Needs
  - Design Inputs
  - Design Outputs
  - VV Protocols
  - Design Reviews
  - Design Transfers
  - Traceability Links

## Dependency Requirements

Ensure these packages are installed in your virtual environment:

```bash
# Core dependencies
Django>=3.2
djangorestframework>=3.12
django-filter>=2.4
django-cors-headers>=3.10

# Optional but recommended
django-extensions>=3.1  # For shell_plus, other utilities
drf-spectacular>=0.20   # For auto-generated API documentation
python-dateutil>=2.8    # For date parsing in serializers
```

Update your `requirements.txt`:

```
Django>=3.2
djangorestframework>=3.12
django-filter>=2.4
django-cors-headers>=3.10
django-extensions>=3.1
drf-spectacular>=0.20
python-dateutil>=2.8
Pillow>=8.0  # For file uploads
psycopg2-binary>=2.9  # If using PostgreSQL
```

Install:

```bash
pip install -r requirements.txt
```

## Database Configuration

### PostgreSQL (Recommended)

If you're using PostgreSQL, ensure you have the PostgreSQL adapter:

```bash
pip install psycopg2-binary
```

Update settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'arni_medica',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### SQLite (Development Only)

For development, SQLite works fine:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## File Upload Configuration

Configure media file handling:

```python
# settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Allowed file types for design documents
FILE_UPLOAD_ALLOWED_TYPES = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
}
```

Update your main `urls.py` to serve media files in development:

```python
# urls.py

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## API Documentation

### With drf-spectacular

Install:

```bash
pip install drf-spectacular
```

Update settings:

```python
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

Add to urls:

```python
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```

Visit `http://localhost:8000/api/docs/` for interactive API documentation.

## Testing

Create test files for design_controls:

```bash
mkdir -p design_controls/tests
touch design_controls/tests/__init__.py
touch design_controls/tests/test_models.py
touch design_controls/tests/test_views.py
touch design_controls/tests/test_serializers.py
```

Example test:

```python
# design_controls/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from design_controls.models import DesignProject

User = get_user_model()

class DesignProjectTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_create_design_project(self):
        project = DesignProject.objects.create(
            title='Test Device',
            product_type='device',
            regulatory_pathway='510k',
            project_lead=self.user
        )
        self.assertEqual(project.project_id, 'DP-0001')
        self.assertEqual(project.status, 'active')
        self.assertEqual(project.current_phase, 'planning')
```

Run tests:

```bash
python manage.py test design_controls
```

## Permissions & Authentication

### Using Token Authentication

Generate tokens for users:

```python
# In Django shell
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='john')
token, created = Token.objects.get_or_create(user=user)
print(token.key)
```

Use in API requests:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/design-controls/design-projects/
```

### Custom Permissions

For role-based access, create custom permission classes:

```python
# design_controls/permissions.py

from rest_framework import permissions

class CanApproveDesignInput(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsProjectLead(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.project_lead == request.user
```

Use in views:

```python
from rest_framework.permissions import IsAuthenticated
from .permissions import CanApproveDesignInput

class DesignInputViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanApproveDesignInput]
```

## Monitoring & Logging

Configure logging:

```python
# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'design_controls.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'design_controls': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Troubleshooting

### Migration Errors

```bash
# Reset migrations (development only!)
python manage.py migrate design_controls zero
python manage.py migrate design_controls

# Check migration status
python manage.py showmigrations design_controls
```

### Import Errors

Ensure all dependencies are imported correctly:

```python
# Check these imports work
from core.models import AuditedModel
from users.models import Department, ProductLine, Site
from documents.models import Document  # if used
```

### Admin Not Showing Up

Restart the development server:

```bash
python manage.py runserver
```

Clear browser cache and refresh the admin page.

### API Returns 403 Forbidden

Check authentication headers:

```bash
# Without auth (should fail if permissions required)
curl http://localhost:8000/api/design-controls/design-projects/

# With token
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/design-controls/design-projects/
```

## Production Deployment

### Gunicorn

```bash
pip install gunicorn
gunicorn arni_medica.wsgi:application --bind 0.0.0.0:8000
```

### Whitenoise for Static Files

```bash
pip install whitenoise
```

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Environment Variables

```bash
# .env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=api.example.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

```python
# settings.py
import os
from pathlib import Path

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

## Backup & Recovery

### Database Backups

```bash
# PostgreSQL dump
pg_dump -U postgres arni_medica > backup.sql

# Restore
psql -U postgres arni_medica < backup.sql

# Django dump data
python manage.py dumpdata design_controls > design_controls_backup.json

# Load data
python manage.py loaddata design_controls_backup.json
```

## Next Steps

1. Review the README.md for complete API documentation
2. Check EXAMPLES.md for usage scenarios
3. Run migrations and start the development server
4. Access admin at `/admin/design_controls/`
5. Test API endpoints using the documentation
6. Create test data and workflows
7. Implement custom permissions as needed
8. Deploy to production when ready

## Support

For issues or questions:

1. Check the README.md documentation
2. Review EXAMPLES.md for usage patterns
3. Check Django and DRF documentation
4. Review application logs
5. Test with Django shell:

```bash
python manage.py shell
from design_controls.models import DesignProject
projects = DesignProject.objects.all()
print(projects)
```
