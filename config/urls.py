from django.http import JsonResponse
from django.db import connection
from django.contrib import admin


def _db_check(request):
    """Diagnostic: check what columns exist in key tables."""
    cursor = connection.cursor()
    result = {}
    for table in ['users_department', 'users_role', 'users_userprofile', 'users_site', 'users_productline']:
        try:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
            result[table] = [r[0] for r in cursor.fetchall()]
        except Exception as e:
            result[table] = str(e)
    # Check ALL migration status
    try:
        cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, id")
        result['all_migrations'] = [f"{r[0]}.{r[1]}" for r in cursor.fetchall()]
    except Exception as e:
        result['all_migrations'] = str(e)
    # Show migration files on disk
    import os
    mig_files = {}
    for app_dir in ['users', 'training', 'forms', 'documents', 'capa', 'complaints',
                     'deviations', 'change_controls', 'suppliers', 'audit_mgmt', 'workflows']:
        mig_path = os.path.join('/app', app_dir, 'migrations')
        if os.path.isdir(mig_path):
            mig_files[app_dir] = sorted([f for f in os.listdir(mig_path) if f.endswith('.py') and f != '__init__.py'])
    result['migration_files_on_disk'] = mig_files
    # Build version
    result['build_marker'] = 'v4-dashboard-fix'
    return JsonResponse(result)


def _run_seed(request):
    """Manually run seed_eqms command."""
    import subprocess
    try:
        proc = subprocess.run(
            ['python', 'manage.py', 'seed_eqms'],
            capture_output=True, text=True, timeout=120, cwd='/app'
        )
        return JsonResponse({
            'returncode': proc.returncode,
            'stdout': proc.stdout[-5000:] if proc.stdout else '',
            'stderr': proc.stderr[-5000:] if proc.stderr else '',
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})


def _run_migrate(request):
    """Manually run migrations and return output."""
    import subprocess
    try:
        proc = subprocess.run(
            ['python', 'manage.py', 'migrate', '--noinput', '-v', '2'],
            capture_output=True, text=True, timeout=120, cwd='/app'
        )
        return JsonResponse({
            'returncode': proc.returncode,
            'stdout': proc.stdout[-5000:] if proc.stdout else '',
            'stderr': proc.stderr[-5000:] if proc.stderr else '',
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # App endpoints
    path('api/users/', include('users.urls')),
    path('api/workflows/', include('workflows.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/capa/', include('capa.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/training/', include('training.urls')),
    path('api/audits/', include('audit_mgmt.urls')),
    path('api/ai/', include('ai_insights.urls')),
    path('api/audit-logs/', include('core.urls')),
    path('api/deviations/', include('deviations.urls')),
    path('api/change-controls/', include('change_controls.urls')),
    path('api/forms/', include('forms.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    # Health check
    path('api/health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
    # DB diagnostic
    path('api/db-check/', lambda r: _db_check(r)),
    path('api/run-migrate/', lambda r: _run_migrate(r)),
    path('api/run-seed/', lambda r: _run_seed(r)),
    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
