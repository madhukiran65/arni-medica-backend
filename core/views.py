from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
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
