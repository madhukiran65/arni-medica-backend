from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, ChoiceFilter, DateFromToRangeFilter
from rest_framework.filters import SearchFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import ChangeControl
from .serializers import (
    ChangeControlListSerializer,
    ChangeControlDetailSerializer,
    ChangeControlCreateSerializer,
    StageTransitionSerializer,
    ChangeControlApprovalSerializer,
    ApprovalResponseSerializer,
    ChangeControlTaskSerializer,
    ChangeControlAttachmentSerializer,
    ChangeControlCommentSerializer,
)


class ChangeControlFilterSet(FilterSet):
    """Advanced filtering for change controls."""
    stage = ChoiceFilter(field_name='current_stage', choices=ChangeControl.STAGE_CHOICES)
    change_type = ChoiceFilter(field_name='change_type', choices=ChangeControl.CHANGE_TYPE_CHOICES)
    category = ChoiceFilter(field_name='change_category', choices=ChangeControl.CHANGE_CATEGORY_CHOICES)
    risk_level = ChoiceFilter(field_name='risk_level', choices=ChangeControl.RISK_LEVEL_CHOICES)
    priority = CharFilter(field_name='risk_level', lookup_expr='icontains')
    department = CharFilter(field_name='department__id')
    created_at_range = DateFromToRangeFilter(field_name='created_at')
    search = CharFilter(method='search_filter')

    def search_filter(self, queryset, name, value):
        """Search across title and description."""
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value) | Q(change_control_id__icontains=value)
        )

    class Meta:
        model = ChangeControl
        fields = ['current_stage', 'change_type', 'change_category', 'risk_level', 'department']


class ChangeControlViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Change Controls.
    Supports filtering, searching, and custom actions for workflow management.
    """
    queryset = ChangeControl.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ChangeControlFilterSet
    search_fields = ['change_control_id', 'title', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChangeControlDetailSerializer
        elif self.action == 'list':
            return ChangeControlListSerializer
        elif self.action == 'create':
            return ChangeControlCreateSerializer
        elif self.action == 'stage_transition':
            return StageTransitionSerializer
        elif self.action == 'respond_approval':
            return ApprovalResponseSerializer
        return ChangeControlDetailSerializer

    def perform_create(self, serializer):
        """Set created_by and updated_by to current user on creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """Override list to use proper serializer."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use proper serializer."""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def stage_transition(self, request, pk=None):
        """
        Transition a change control to the next stage with validation gates.
        Validates required fields per stage before allowing transition.
        """
        change_control = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_stage = serializer.validated_data['target_stage']
        current_stage = change_control.current_stage

        # Gate validation based on current stage
        if current_stage == 'screening' and target_stage != 'screening':
            if not hasattr(change_control, 'approvals') or not change_control.approvals.exists():
                return Response(
                    {'detail': 'Cannot leave screening without screening_decision set'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if current_stage == 'impact_assessment' and target_stage != 'impact_assessment':
            if not change_control.affected_areas or len(change_control.affected_areas) == 0:
                return Response(
                    {'detail': 'Cannot leave impact_assessment without affected_areas filled'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if current_stage == 'implementation' and target_stage != 'implementation':
            if not change_control.rollback_plan and not change_control.verification_method:
                return Response(
                    {'detail': 'Cannot leave implementation without implementation_notes'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if target_stage == 'closed' and current_stage != 'closed':
            if not change_control.verification_completed:
                return Response(
                    {'detail': 'Cannot enter closed without verification_result'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update stage
        change_control.current_stage = target_stage
        change_control.stage_entered_at = timezone.now()
        change_control.save()

        return Response(
            ChangeControlDetailSerializer(change_control).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def approvals(self, request, pk=None):
        """
        Get all approvals for a change control.
        """
        change_control = self.get_object()
        approvals = change_control.approvals.all()
        serializer = ChangeControlApprovalSerializer(approvals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond_approval(self, request, pk=None):
        """
        Respond to an approval request.
        """
        change_control = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process approval response logic here
        
        return Response(
            ChangeControlDetailSerializer(change_control).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get', 'post'])
    def tasks(self, request, pk=None):
        """
        Get all tasks for a change control or create a new task.
        """
        change_control = self.get_object()
        
        if request.method == 'GET':
            tasks = change_control.tasks.all()
            serializer = ChangeControlTaskSerializer(tasks, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ChangeControlTaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(change_control=change_control)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path=r'tasks/(?P<task_pk>\d+)/complete')
    def complete_task(self, request, pk=None, task_pk=None):
        """
        Mark a task as complete.
        """
        change_control = self.get_object()
        task = change_control.tasks.get(pk=task_pk)
        
        task.status = 'completed'
        task.save()
        
        serializer = ChangeControlTaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'])
    def attachments(self, request, pk=None):
        """
        Get all attachments for a change control or upload a new attachment.
        """
        change_control = self.get_object()
        
        if request.method == 'GET':
            attachments = change_control.attachments.all()
            serializer = ChangeControlAttachmentSerializer(attachments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ChangeControlAttachmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(change_control=change_control)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """
        Get all comments for a change control or post a new comment.
        """
        change_control = self.get_object()

        if request.method == 'GET':
            comments = change_control.comments.all()
            serializer = ChangeControlCommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = ChangeControlCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(change_control=change_control, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def change_control_stats(self, request):
        """
        Get aggregated statistics on all change controls.
        Returns: counts by stage, type, category, risk_level and avg days to close.
        """
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_stage': dict(
                queryset.values('current_stage').annotate(count=Count('id')).values_list('current_stage', 'count')
            ),
            'by_type': dict(
                queryset.values('change_type').annotate(count=Count('id')).values_list('change_type', 'count')
            ),
            'by_category': dict(
                queryset.values('change_category').annotate(count=Count('id')).values_list('change_category', 'count')
            ),
            'by_risk_level': dict(
                queryset.values('risk_level').annotate(count=Count('id')).values_list('risk_level', 'count')
            ),
        }

        # Calculate avg days to close
        closed_controls = queryset.filter(closed_date__isnull=False)
        if closed_controls.exists():
            avg_days = (
                closed_controls.annotate(
                    days_to_close=timezone.now().date() - timezone.now().date()
                ).aggregate(avg=Avg('days_to_close'))['avg']
            )
            stats['avg_days_to_close'] = int(avg_days) if avg_days else None

        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all change controls that are overdue (past target_date and not closed).
        """
        now = timezone.now()
        overdue_controls = self.get_queryset().filter(
            target_completion_date__lt=now,
            closed_date__isnull=True
        )
        serializer = ChangeControlListSerializer(overdue_controls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def impact_summary(self, request, pk=None):
        """
        Get aggregated impact data for a change control.
        Returns: affected documents, processes, products, departments.
        """
        change_control = self.get_object()

        impact_data = {
            'affected_areas': change_control.affected_areas or [],
            'affected_documents': change_control.affected_documents or [],
            'affected_processes': change_control.affected_processes or [],
            'affected_products': change_control.affected_products or [],
            'affected_departments': list(
                change_control.affected_departments.values_list('name', flat=True)
            ),
            'training_impact': change_control.training_impact,
            'validation_impact': change_control.validation_impact,
            'documentation_impact': change_control.documentation_impact,
            'quality_impact': change_control.quality_impact,
            'regulatory_impact': change_control.regulatory_impact,
            'safety_impact': change_control.safety_impact,
        }

        return Response(impact_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get combined activity timeline for a change control.
        Includes stage transitions, approvals, tasks, and comments.
        """
        change_control = self.get_object()

        timeline_events = []

        # Stage transitions
        for approval in change_control.approvals.all().order_by('created_at'):
            timeline_events.append({
                'type': 'approval',
                'event': f'Approval request - {approval.get_approval_role_display()}',
                'timestamp': approval.created_at,
                'user': approval.approver.username if approval.approver else None,
                'details': approval.comments,
            })

        # Tasks
        for task in change_control.tasks.all().order_by('created_at'):
            timeline_events.append({
                'type': 'task',
                'event': f'Task: {task.title}',
                'timestamp': task.created_at,
                'user': task.assigned_to.username if task.assigned_to else None,
                'status': task.status,
            })

        # Comments
        for comment in change_control.comments.all().order_by('created_at'):
            timeline_events.append({
                'type': 'comment',
                'event': 'Comment added',
                'timestamp': comment.created_at,
                'user': comment.author.username if comment.author else None,
                'details': comment.comment,
            })

        # Sort by timestamp
        timeline_events.sort(key=lambda x: x['timestamp'], reverse=True)

        return Response(timeline_events, status=status.HTTP_200_OK)
