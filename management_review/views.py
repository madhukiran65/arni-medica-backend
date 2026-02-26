"""
Management Review & Analytics Dashboard Views

RESTful API endpoints for all management review models with filtering,
searching, and the special DashboardAPIView for aggregated analytics.
"""

from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters import FilterSet, CharFilter, BooleanFilter, DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F, Case, When, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    QualityMetric,
    MetricSnapshot,
    QualityObjective,
    ManagementReviewMeeting,
    ManagementReviewItem,
    ManagementReviewAction,
    ManagementReviewReport,
    DashboardConfiguration,
)
from .serializers import (
    QualityMetricListSerializer,
    QualityMetricDetailSerializer,
    MetricSnapshotListSerializer,
    MetricSnapshotDetailSerializer,
    QualityObjectiveListSerializer,
    QualityObjectiveDetailSerializer,
    ManagementReviewMeetingListSerializer,
    ManagementReviewMeetingDetailSerializer,
    ManagementReviewItemListSerializer,
    ManagementReviewItemDetailSerializer,
    ManagementReviewActionListSerializer,
    ManagementReviewActionDetailSerializer,
    ManagementReviewReportListSerializer,
    ManagementReviewReportDetailSerializer,
    DashboardConfigurationSerializer,
)


# ============================================================================
# FILTER SETS
# ============================================================================

class QualityMetricFilterSet(FilterSet):
    """Advanced filtering for quality metrics."""

    module = CharFilter(field_name='module', lookup_expr='exact')
    calculation_method = CharFilter(field_name='calculation_method', lookup_expr='exact')
    trend = CharFilter(field_name='trend_direction', lookup_expr='exact')
    is_active = BooleanFilter(field_name='is_active')
    search = CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        """Search across metric_id, name, and description."""
        if value:
            return queryset.filter(
                Q(metric_id__icontains=value) |
                Q(name__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset

    class Meta:
        model = QualityMetric
        fields = ['module', 'calculation_method', 'trend', 'is_active']


class MetricSnapshotFilterSet(FilterSet):
    """Advanced filtering for metric snapshots."""

    metric = CharFilter(field_name='metric__metric_id', lookup_expr='exact')
    period_type = CharFilter(field_name='period_type', lookup_expr='exact')
    snapshot_date_range = DateFromToRangeFilter(field_name='snapshot_date')

    class Meta:
        model = MetricSnapshot
        fields = ['metric', 'period_type']


class QualityObjectiveFilterSet(FilterSet):
    """Advanced filtering for quality objectives."""

    status = CharFilter(field_name='status', lookup_expr='exact')
    owner = CharFilter(field_name='owner__id', lookup_expr='exact')
    department = CharFilter(field_name='department__id', lookup_expr='exact')
    fiscal_year = CharFilter(field_name='fiscal_year', lookup_expr='exact')
    target_date_range = DateFromToRangeFilter(field_name='target_date')
    search = CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        """Search across objective_id, title, and description."""
        if value:
            return queryset.filter(
                Q(objective_id__icontains=value) |
                Q(title__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset

    class Meta:
        model = QualityObjective
        fields = ['status', 'owner', 'department', 'fiscal_year']


class ManagementReviewMeetingFilterSet(FilterSet):
    """Advanced filtering for management review meetings."""

    meeting_type = CharFilter(field_name='meeting_type', lookup_expr='exact')
    status = CharFilter(field_name='status', lookup_expr='exact')
    chairperson = CharFilter(field_name='chairperson__id', lookup_expr='exact')
    meeting_date_range = DateFromToRangeFilter(field_name='meeting_date')
    search = CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        """Search across meeting_id and title."""
        if value:
            return queryset.filter(
                Q(meeting_id__icontains=value) |
                Q(title__icontains=value)
            )
        return queryset

    class Meta:
        model = ManagementReviewMeeting
        fields = ['meeting_type', 'status', 'chairperson']


class ManagementReviewItemFilterSet(FilterSet):
    """Advanced filtering for management review items."""

    meeting = CharFilter(field_name='meeting__meeting_id', lookup_expr='exact')
    category = CharFilter(field_name='category', lookup_expr='exact')
    presenter = CharFilter(field_name='presenter__id', lookup_expr='exact')

    class Meta:
        model = ManagementReviewItem
        fields = ['meeting', 'category', 'presenter']


class ManagementReviewActionFilterSet(FilterSet):
    """Advanced filtering for management review actions."""

    status = CharFilter(field_name='status', lookup_expr='exact')
    priority = CharFilter(field_name='priority', lookup_expr='exact')
    assigned_to = CharFilter(field_name='assigned_to__id', lookup_expr='exact')
    meeting = CharFilter(field_name='meeting__meeting_id', lookup_expr='exact')
    due_date_range = DateFromToRangeFilter(field_name='due_date')
    is_overdue = BooleanFilter(method='filter_is_overdue')
    search = CharFilter(method='filter_search')

    def filter_is_overdue(self, queryset, name, value):
        """Filter for overdue actions."""
        if value is True:
            return queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['open', 'in_progress']
            )
        elif value is False:
            return queryset.exclude(
                due_date__lt=timezone.now().date(),
                status__in=['open', 'in_progress']
            )
        return queryset

    def filter_search(self, queryset, name, value):
        """Search across action_id and description."""
        if value:
            return queryset.filter(
                Q(action_id__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset

    class Meta:
        model = ManagementReviewAction
        fields = ['status', 'priority', 'assigned_to', 'meeting']


class ManagementReviewReportFilterSet(FilterSet):
    """Advanced filtering for management review reports."""

    status = CharFilter(field_name='status', lookup_expr='exact')
    approved_by = CharFilter(field_name='approved_by__id', lookup_expr='exact')
    quality_assessment = CharFilter(field_name='overall_quality_assessment', lookup_expr='exact')

    class Meta:
        model = ManagementReviewReport
        fields = ['status', 'approved_by', 'quality_assessment']


# ============================================================================
# VIEWSETS
# ============================================================================

class QualityMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quality metrics."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QualityMetricFilterSet
    search_fields = ['metric_id', 'name', 'description']
    ordering_fields = ['display_order', 'metric_id', 'name', 'last_calculated']
    ordering = ['display_order', 'metric_id']

    def get_queryset(self):
        return QualityMetric.objects.filter(is_active=True).order_by('display_order')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QualityMetricDetailSerializer
        return QualityMetricListSerializer


class MetricSnapshotViewSet(viewsets.ModelViewSet):
    """ViewSet for managing metric snapshots."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MetricSnapshotFilterSet
    ordering_fields = ['-snapshot_date', 'metric', 'value']
    ordering = ['-snapshot_date']

    def get_queryset(self):
        return MetricSnapshot.objects.select_related('metric').order_by('-snapshot_date')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MetricSnapshotDetailSerializer
        return MetricSnapshotListSerializer


class QualityObjectiveViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quality objectives."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QualityObjectiveFilterSet
    search_fields = ['objective_id', 'title', 'description']
    ordering_fields = ['created_at', 'objective_id', 'target_date', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return QualityObjective.objects.select_related(
            'owner', 'department', 'target_metric'
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QualityObjectiveDetailSerializer
        return QualityObjectiveListSerializer


class ManagementReviewMeetingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing management review meetings."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ManagementReviewMeetingFilterSet
    search_fields = ['meeting_id', 'title']
    ordering_fields = ['-meeting_date', 'meeting_id', 'title', 'status']
    ordering = ['-meeting_date']

    def get_queryset(self):
        return ManagementReviewMeeting.objects.select_related(
            'chairperson'
        ).prefetch_related('attendees').order_by('-meeting_date')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ManagementReviewMeetingDetailSerializer
        return ManagementReviewMeetingListSerializer

    @action(detail=True, methods=['post'])
    def start_meeting(self, request, pk=None):
        """Start a management review meeting."""
        meeting = self.get_object()
        if meeting.status == 'planned':
            meeting.status = 'in_progress'
            meeting.save(update_fields=['status', 'updated_at'])
            return Response(
                {'detail': 'Meeting started successfully.'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Meeting can only be started from planned status.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def complete_meeting(self, request, pk=None):
        """Complete a management review meeting."""
        meeting = self.get_object()
        if meeting.status in ['planned', 'in_progress']:
            meeting.status = 'completed'
            meeting.save(update_fields=['status', 'updated_at'])
            return Response(
                {'detail': 'Meeting completed successfully.'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Meeting can only be completed from planned or in_progress status.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ManagementReviewItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing management review items."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ManagementReviewItemFilterSet
    ordering_fields = ['meeting', 'item_number', 'category']
    ordering = ['meeting', 'item_number']

    def get_queryset(self):
        return ManagementReviewItem.objects.select_related(
            'meeting', 'presenter'
        ).order_by('meeting', 'item_number')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ManagementReviewItemDetailSerializer
        return ManagementReviewItemListSerializer


class ManagementReviewActionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing management review actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ManagementReviewActionFilterSet
    search_fields = ['action_id', 'description']
    ordering_fields = ['-due_date', 'action_id', 'status', 'priority']
    ordering = ['-due_date']

    def get_queryset(self):
        return ManagementReviewAction.objects.select_related(
            'meeting', 'review_item', 'assigned_to', 'linked_capa', 'linked_change_control'
        ).order_by('-due_date')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ManagementReviewActionDetailSerializer
        return ManagementReviewActionListSerializer

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark an action as complete."""
        action_obj = self.get_object()
        action_obj.status = 'completed'
        action_obj.completion_date = timezone.now().date()
        action_obj.completion_notes = request.data.get('completion_notes', '')
        action_obj.save()
        return Response(
            ManagementReviewActionDetailSerializer(action_obj).data,
            status=status.HTTP_200_OK
        )


class ManagementReviewReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing management review reports."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ManagementReviewReportFilterSet
    ordering_fields = ['-created_at', 'report_id', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return ManagementReviewReport.objects.select_related(
            'meeting', 'approved_by', 'linked_document'
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ManagementReviewReportDetailSerializer
        return ManagementReviewReportListSerializer

    @action(detail=True, methods=['post'])
    def approve_report(self, request, pk=None):
        """Approve a management review report."""
        report = self.get_object()
        if report.status != 'draft':
            return Response(
                {'detail': 'Only draft reports can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report.status = 'approved'
        report.approved_by = request.user
        report.approval_date = timezone.now()
        report.save()
        return Response(
            ManagementReviewReportDetailSerializer(report).data,
            status=status.HTTP_200_OK
        )


class DashboardConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user dashboard configurations."""

    permission_classes = [IsAuthenticated]
    serializer_class = DashboardConfigurationSerializer

    def get_queryset(self):
        # Users can only see their own dashboard configuration
        return DashboardConfiguration.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_config(self, request):
        """Get or create the current user's dashboard configuration."""
        config, created = DashboardConfiguration.objects.get_or_create(
            user=request.user
        )
        serializer = self.get_serializer(config)
        return Response(serializer.data)


# ============================================================================
# SPECIAL DASHBOARD API VIEW (NOT A VIEWSET)
# ============================================================================

class DashboardAPIView(APIView):
    """
    Special aggregated dashboard view that provides key metrics across all eQMS modules.

    Returns aggregated data for executive dashboard including:
    - Open CAPAs count
    - Open complaints count
    - Overdue trainings count
    - Open deviations count
    - Pending change controls count
    - Open audit findings count
    - Total documents count
    - Active suppliers count
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get aggregated dashboard data."""

        try:
            # Import models from other modules
            from capa.models import CAPA
            from complaints.models import Complaint
            from deviations.models import Deviation
            from change_controls.models import ChangeControl
            from documents.models import Document
            from suppliers.models import Supplier
            from audit_mgmt.models import AuditFinding
            from documents.models import Training

            # Calculate all metrics
            dashboard_data = {
                'timestamp': timezone.now(),
                'metrics': {}
            }

            # CAPA Metrics
            open_capas = CAPA.objects.filter(
                current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan', 'implementation', 'effectiveness'],
                is_active=True
            ).count()
            dashboard_data['metrics']['open_capas'] = open_capas

            # Complaint Metrics
            try:
                open_complaints = Complaint.objects.filter(
                    status__in=['open', 'under_investigation', 'pending_closure'],
                    is_active=True
                ).count()
            except:
                open_complaints = 0
            dashboard_data['metrics']['open_complaints'] = open_complaints

            # Deviation Metrics
            open_deviations = Deviation.objects.filter(
                status__in=['open', 'under_investigation', 'pending_closure'],
                is_active=True
            ).count()
            dashboard_data['metrics']['open_deviations'] = open_deviations

            # Change Control Metrics
            pending_change_controls = ChangeControl.objects.filter(
                status__in=['pending', 'approved_pending_implementation'],
                is_active=True
            ).count()
            dashboard_data['metrics']['pending_change_controls'] = pending_change_controls

            # Document Metrics
            total_documents = Document.objects.filter(is_active=True).count()
            dashboard_data['metrics']['total_documents'] = total_documents

            # Supplier Metrics
            active_suppliers = Supplier.objects.filter(status='active').count()
            dashboard_data['metrics']['active_suppliers'] = active_suppliers

            # Audit Findings Metrics
            try:
                open_audit_findings = AuditFinding.objects.filter(
                    status__in=['open', 'pending_closure'],
                    is_active=True
                ).count()
            except:
                open_audit_findings = 0
            dashboard_data['metrics']['open_audit_findings'] = open_audit_findings

            # Training Metrics - count overdue trainings
            try:
                overdue_trainings = Training.objects.filter(
                    due_date__lt=timezone.now().date(),
                    status__in=['not_started', 'in_progress'],
                    is_active=True
                ).count()
            except:
                overdue_trainings = 0
            dashboard_data['metrics']['overdue_trainings'] = overdue_trainings

            # Management Review specific metrics
            open_mr_actions = ManagementReviewAction.objects.filter(
                status__in=['open', 'in_progress'],
                is_active=True
            ).count()
            dashboard_data['metrics']['open_mr_actions'] = open_mr_actions

            overdue_mr_actions = ManagementReviewAction.objects.filter(
                due_date__lt=timezone.now().date(),
                status__in=['open', 'in_progress'],
                is_active=True
            ).count()
            dashboard_data['metrics']['overdue_mr_actions'] = overdue_mr_actions

            # Quality objectives status
            objectives_on_track = QualityObjective.objects.filter(
                status='on_track',
                is_active=True
            ).count()
            objectives_at_risk = QualityObjective.objects.filter(
                status='at_risk',
                is_active=True
            ).count()
            objectives_achieved = QualityObjective.objects.filter(
                status='achieved',
                is_active=True
            ).count()

            dashboard_data['metrics']['objectives_on_track'] = objectives_on_track
            dashboard_data['metrics']['objectives_at_risk'] = objectives_at_risk
            dashboard_data['metrics']['objectives_achieved'] = objectives_achieved

            # Recent meetings
            recent_meetings = ManagementReviewMeeting.objects.filter(
                is_active=True
            ).order_by('-meeting_date')[:5]

            dashboard_data['recent_meetings'] = [
                {
                    'id': m.id,
                    'meeting_id': m.meeting_id,
                    'title': m.title,
                    'meeting_date': m.meeting_date,
                    'status': m.status,
                }
                for m in recent_meetings
            ]

            # System health summary
            dashboard_data['system_health'] = {
                'total_open_items': (
                    open_capas + open_complaints + open_deviations +
                    pending_change_controls + open_audit_findings
                ),
                'total_overdue_items': (overdue_mr_actions + overdue_trainings),
                'objectives_at_risk_count': objectives_at_risk,
            }

            return Response(dashboard_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Return graceful error response if module imports fail
            return Response(
                {
                    'error': 'Failed to retrieve dashboard metrics',
                    'detail': str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
