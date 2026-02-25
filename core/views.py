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
