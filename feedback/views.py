from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count

from .models import FeedbackTicket
from .serializers import (
    FeedbackTicketListSerializer,
    FeedbackTicketDetailSerializer,
    FeedbackTicketCreateSerializer,
)


class FeedbackTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'status', 'priority', 'module']
    search_fields = ['ticket_id', 'title', 'description']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackTicketCreateSerializer
        if self.action == 'list':
            return FeedbackTicketListSerializer
        return FeedbackTicketDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = FeedbackTicket.objects.prefetch_related('attachments').select_related(
            'submitted_by', 'assigned_to'
        )
        # Admins see all, regular users see only their own
        if self._is_admin(user):
            return qs
        return qs.filter(submitted_by=user)

    # ── Custom actions ──

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Current user's submitted tickets."""
        tickets = FeedbackTicket.objects.filter(
            submitted_by=request.user
        ).select_related('assigned_to').order_by('-created_at')
        serializer = FeedbackTicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Admin assigns a ticket to a user."""
        ticket = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        if assigned_to_id:
            ticket.assigned_to_id = assigned_to_id
            ticket.status = 'in_progress'
            ticket.updated_by = request.user
            ticket.save(update_fields=['assigned_to', 'status', 'updated_by', 'updated_at'])
        return Response(FeedbackTicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a ticket as resolved with resolution summary."""
        ticket = self.get_object()
        ticket.status = 'resolved'
        ticket.resolution_summary = request.data.get('resolution_summary', '')
        ticket.resolved_at = timezone.now()
        ticket.updated_by = request.user
        ticket.save(update_fields=[
            'status', 'resolution_summary', 'resolved_at', 'updated_by', 'updated_at'
        ])
        return Response(FeedbackTicketDetailSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a resolved ticket."""
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.updated_by = request.user
        ticket.save(update_fields=['status', 'updated_by', 'updated_at'])
        return Response(FeedbackTicketDetailSerializer(ticket).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Ticket statistics for admin dashboard."""
        qs = FeedbackTicket.objects.all()
        return Response({
            'total': qs.count(),
            'by_status': list(qs.values('status').annotate(count=Count('id'))),
            'by_type': list(qs.values('type').annotate(count=Count('id'))),
            'by_priority': list(qs.values('priority').annotate(count=Count('id'))),
            'by_module': list(qs.values('module').annotate(count=Count('id'))),
        })

    # ── Helpers ──

    def _is_admin(self, user):
        if user.is_superuser:
            return True
        try:
            return user.profile.roles.filter(
                name__in=['Super Admin', 'Doc Control Admin']
            ).exists()
        except Exception:
            return False
