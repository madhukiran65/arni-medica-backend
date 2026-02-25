from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection
from django.conf import settings
from core.models import AuditLog
from core.serializers import AuditLogSerializer
from core.permissions import CanViewAuditTrail


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only audit log (21 CFR Part 11). No create/update/delete via API."""
    queryset = AuditLog.objects.select_related('user', 'content_type').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, CanViewAuditTrail]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'content_type']
    search_fields = ['object_repr', 'change_summary']
    ordering_fields = ['timestamp', 'action']


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Verifies database connectivity and service status.
    """
    database_status = 'healthy'
    try:
        connection.ensure_connection()
    except Exception as e:
        database_status = 'unhealthy'

    overall_status = 'healthy' if database_status == 'healthy' else 'degraded'

    return Response({
        'status': overall_status,
        'database': database_status,
        'version': '1.0.0',
        'app': 'Arni Medica eQMS',
        'debug': settings.DEBUG,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def setup_initial_data(request):
    """
    One-time setup endpoint to create superuser and seed reference data.
    Protected by setup secret key.
    """
    setup_key = request.data.get('setup_key', '')
    if setup_key != 'arni-medica-setup-2026':
        return Response({'error': 'Invalid setup key'}, status=403)

    from django.contrib.auth.models import User
    from django.core.management import call_command
    import io

    results = {}

    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@arnimedica.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        results['superuser'] = 'Created admin user'
    else:
        results['superuser'] = 'Admin user already exists'

    # Create additional test users
    test_users = [
        ('qa_manager', 'qa@arnimedica.com', 'QA', 'Manager'),
        ('doc_controller', 'docs@arnimedica.com', 'Document', 'Controller'),
        ('training_admin', 'training@arnimedica.com', 'Training', 'Admin'),
        ('capa_owner', 'capa@arnimedica.com', 'CAPA', 'Owner'),
    ]
    users_created = 0
    for username, email, first, last in test_users:
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username, email=email, password='test123',
                first_name=first, last_name=last
            )
            users_created += 1
    results['test_users'] = f'Created {users_created} test users'

    # Run seed data command
    output = io.StringIO()
    try:
        call_command('seed_data', stdout=output)
        results['seed_data'] = output.getvalue().strip()
    except Exception as e:
        results['seed_data'] = f'Error: {str(e)}'

    return Response(results)
