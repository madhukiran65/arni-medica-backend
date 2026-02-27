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
                     'deviations', 'change_controls', 'suppliers', 'audit_mgmt', 'workflows',
                     'risk_management', 'design_controls', 'equipment', 'batch_records',
                     'validation_mgmt', 'management_review']:
        mig_path = os.path.join('/app', app_dir, 'migrations')
        if os.path.isdir(mig_path):
            mig_files[app_dir] = sorted([f for f in os.listdir(mig_path) if f.endswith('.py') and f != '__init__.py'])
    result['migration_files_on_disk'] = mig_files
    # Build version
    result['build_marker'] = 'v22-cleanup-fix'
    return JsonResponse(result)


def _run_mgmt(request):
    """Run any management command. Usage: /api/run-mgmt/?cmd=enrich_demo_data"""
    import subprocess
    command = request.GET.get('cmd', '')
    if not command:
        return JsonResponse({'error': 'Missing ?cmd= parameter'})
    allowed = ['enrich_demo_data', 'seed_form_templates', 'seed_demo_data', 'seed_eqms', 'seed_data', 'add_superseded_stage', 'cleanup_dummy_users', 'migrate', 'showmigrations']
    if command not in allowed:
        return JsonResponse({'error': f'Command not allowed. Allowed: {allowed}'})
    cmd = ['python', 'manage.py', command]
    if command == 'migrate':
        cmd.append('--noinput')
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd='/app')
        return JsonResponse({
            'command': command,
            'returncode': proc.returncode,
            'stdout': proc.stdout[-5000:] if proc.stdout else '',
            'stderr': proc.stderr[-5000:] if proc.stderr else '',
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})


def _run_seed(request):
    """Manually run seed_eqms command. Supports ?demo=1&reset-demo=1&reset-workflows=1."""
    import subprocess
    cmd = ['python', 'manage.py', 'seed_eqms']
    if request.GET.get('demo'):
        cmd.append('--demo')
    if request.GET.get('reset-demo'):
        cmd.append('--reset-demo')
    if request.GET.get('reset-workflows'):
        cmd.append('--reset-workflows')
    try:
        proc = subprocess.run(
            cmd,
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
    """Manually run migrations and return output. ?fake=1 to fake-apply."""
    import subprocess
    cmd = ['python', 'manage.py', 'migrate', '--noinput', '-v', '2']
    if request.GET.get('fake'):
        cmd = ['python', 'manage.py', 'migrate', '--fake', '--noinput', '-v', '2']
    if request.GET.get('app'):
        cmd.append(request.GET['app'])
    if request.GET.get('name'):
        cmd.append(request.GET['name'])
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, cwd='/app'
        )
        return JsonResponse({
            'cmd': ' '.join(cmd),
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
    # New modules (BRD Gap Analysis - Feb 2026)
    path('api/risk-management/', include('risk_management.urls')),
    path('api/design-controls/', include('design_controls.urls')),
    path('api/equipment/', include('equipment.urls')),
    path('api/batch-records/', include('batch_records.urls')),
    path('api/validation/', include('validation_mgmt.urls')),
    path('api/management-review/', include('management_review.urls')),
    path('api/feedback/', include('feedback.urls')),
    # Health check
    path('api/health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
    # DB diagnostic
    path('api/db-check/', lambda r: _db_check(r)),
    path('api/run-migrate/', lambda r: _run_migrate(r)),
    path('api/run-seed/', lambda r: _run_seed(r)),
    path('api/run-mgmt/', lambda r: _run_mgmt(r)),
    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
