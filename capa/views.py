from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import FilterSet, CharFilter, BooleanFilter, DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Count, Q, F, Case, When, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta

from .models import CAPA, CAPAApproval, CAPADocument, CAPAComment
from .serializers import (
    CAPAListSerializer,
    CAPADetailSerializer,
    CAPACreateSerializer,
    CAPAApprovalSerializer,
    ApprovalResponseSerializer,
    CAPADocumentSerializer,
    CAPACommentSerializer,
    PhaseTransitionSerializer,
    RiskMatrixSerializer,
    FiveWAnalysisSerializer,
    ExtensionRequestSerializer,
)


class CAPAFilterSet(FilterSet):
    """Advanced filtering for CAPA objects."""

    current_phase = CharFilter(field_name='current_phase', lookup_expr='exact')
    capa_type = CharFilter(field_name='capa_type', lookup_expr='exact')
    priority = CharFilter(field_name='priority', lookup_expr='exact')
    source = CharFilter(field_name='source', lookup_expr='exact')
    category = CharFilter(field_name='category', lookup_expr='exact')
    department = CharFilter(field_name='department__id', lookup_expr='exact')
    assigned_to = CharFilter(field_name='assigned_to__id', lookup_expr='exact')
    coordinator = CharFilter(field_name='coordinator__id', lookup_expr='exact')
    is_overdue = BooleanFilter(method='filter_is_overdue')
    has_extension = BooleanFilter(field_name='has_extension')
    created_at_range = DateFromToRangeFilter(field_name='created_at')
    target_completion_date_range = DateFromToRangeFilter(field_name='target_completion_date')
    search = CharFilter(method='filter_search')

    def filter_is_overdue(self, queryset, name, value):
        """Filter for overdue CAPAs (past target date and not closed)."""
        if value is True:
            return queryset.filter(
                target_completion_date__lt=timezone.now().date(),
                current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan', 'implementation', 'effectiveness']
            )
        elif value is False:
            return queryset.exclude(
                target_completion_date__lt=timezone.now().date(),
                current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan', 'implementation', 'effectiveness']
            )
        return queryset

    def filter_search(self, queryset, name, value):
        """Search across title, capa_id, and description."""
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(capa_id__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset

    class Meta:
        model = CAPA
        fields = [
            'current_phase', 'capa_type', 'priority', 'source', 'category',
            'department', 'assigned_to', 'coordinator', 'is_overdue', 'has_extension'
        ]


class CAPAViewSet(viewsets.ModelViewSet):
    """ViewSet for managing CAPAs with full lifecycle management."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CAPAFilterSet
    search_fields = ['capa_id', 'title', 'description']
    ordering_fields = ['created_at', 'capa_id', 'title', 'priority', 'target_completion_date']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = CAPA.objects.select_related(
            'department',
            'responsible_person',
            'assigned_to',
            'coordinator',
            'created_by',
            'updated_by',
        ).prefetch_related(
            Prefetch('approvals', queryset=CAPAApproval.objects.select_related('approver')),
            Prefetch('documents', queryset=CAPADocument.objects.select_related('uploaded_by')),
            Prefetch('comments', queryset=CAPAComment.objects.select_related('author').order_by('-created_at'))
        ).all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CAPAListSerializer
        elif self.action == 'retrieve':
            return CAPADetailSerializer
        elif self.action == 'create':
            return CAPACreateSerializer
        elif self.action == 'phase_transition':
            return PhaseTransitionSerializer
        elif self.action == 'update_risk_matrix':
            return RiskMatrixSerializer
        elif self.action == 'update_five_w':
            return FiveWAnalysisSerializer
        elif self.action == 'request_extension':
            return ExtensionRequestSerializer
        elif self.action == 'respond_approval':
            return ApprovalResponseSerializer
        return CAPADetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def phase_transition(self, request, pk=None):
        """Transition to new phase with gate validation."""
        capa = self.get_object()
        serializer = PhaseTransitionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                new_phase = serializer.validated_data['new_phase']
                current_phase = capa.current_phase

                # Gate validation: Check requirements before leaving a phase
                if current_phase == 'investigation':
                    # Can't leave investigation without 5W analysis completed
                    if not all([capa.what_happened, capa.when_happened, capa.where_happened,
                               capa.who_affected, capa.why_happened]):
                        return Response(
                            {'error': '5W Analysis incomplete. All fields required: what, when, where, who, why'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                elif current_phase == 'root_cause':
                    # Can't leave root_cause without root_cause and analysis_method filled
                    if not capa.root_cause or not capa.root_cause_analysis_method:
                        return Response(
                            {'error': 'Root cause and analysis method are required'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                elif current_phase == 'capa_plan':
                    # Can't leave capa_plan without planned_actions having at least one entry
                    if not capa.planned_actions or len(capa.planned_actions) == 0:
                        return Response(
                            {'error': 'At least one planned action is required'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                elif current_phase == 'effectiveness':
                    # Can't enter closure without effectiveness_result being set
                    if new_phase == 'closure' and capa.effectiveness_result == 'pending':
                        return Response(
                            {'error': 'Effectiveness result must be set before closure'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Perform transition
                capa.transition_to(new_phase, user=request.user)
                return Response(CAPADetailSerializer(capa).data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_risk_matrix(self, request, pk=None):
        capa = self.get_object()
        serializer = RiskMatrixSerializer(data=request.data)
        if serializer.is_valid():
            try:
                capa.risk_severity = serializer.validated_data.get('risk_severity', capa.risk_severity)
                capa.risk_occurrence = serializer.validated_data.get('risk_occurrence', capa.risk_occurrence)
                capa.risk_detection = serializer.validated_data.get('risk_detection', capa.risk_detection)
                capa.updated_by = request.user
                capa.save()
                return Response(CAPADetailSerializer(capa).data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'patch'])
    def update_five_w(self, request, pk=None):
        capa = self.get_object()
        serializer = FiveWAnalysisSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                for field in ['why_happened', 'what_happened', 'when_happened', 'where_happened', 'who_affected', 'how_discovered']:
                    if field in data:
                        setattr(capa, field, data[field])
                capa.updated_by = request.user
                capa.save()
                return Response(CAPADetailSerializer(capa).data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def request_extension(self, request, pk=None):
        capa = self.get_object()
        serializer = ExtensionRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                capa.extension_new_due_date = serializer.validated_data.get('extension_new_due_date')
                capa.extension_reason = serializer.validated_data.get('extension_reason', '')
                capa.has_extension = True
                capa.updated_by = request.user
                capa.save()
                return Response(CAPADetailSerializer(capa).data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def approvals(self, request, pk=None):
        capa = self.get_object()
        approvals = capa.approvals.filter(phase=capa.current_phase)
        serializer = CAPAApprovalSerializer(approvals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond_approval(self, request, pk=None):
        capa = self.get_object()
        serializer = ApprovalResponseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                approval = CAPAApproval.objects.get(id=serializer.validated_data['approval_id'], capa=capa)
                approval.status = serializer.validated_data['status']
                approval.approver = request.user
                approval.comments = serializer.validated_data.get('comments', '')
                approval.save()
                return Response(CAPAApprovalSerializer(approval).data)
            except CAPAApproval.DoesNotExist:
                return Response({'error': 'Approval not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        """Get or upload supporting documents."""
        capa = self.get_object()
        if request.method == 'GET':
            serializer = CAPADocumentSerializer(capa.documents.all(), many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            try:
                document = CAPADocument.objects.create(
                    capa=capa,
                    file=request.FILES.get('file'),
                    document_type=request.data.get('document_type', 'other'),
                    title=request.data.get('title', ''),
                    phase=request.data.get('phase', capa.current_phase),
                    description=request.data.get('description', ''),
                    uploaded_by=request.user
                )
                return Response(CAPADocumentSerializer(document).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """Upload supporting document to a CAPA with phase association."""
        capa = self.get_object()
        try:
            if 'file' not in request.FILES:
                return Response({'error': 'File is required'}, status=status.HTTP_400_BAD_REQUEST)

            document = CAPADocument.objects.create(
                capa=capa,
                file=request.FILES['file'],
                document_type=request.data.get('document_type', 'other'),
                title=request.data.get('title', request.FILES['file'].name),
                phase=request.data.get('phase', capa.current_phase),
                description=request.data.get('description', ''),
                uploaded_by=request.user
            )
            return Response(CAPADocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        capa = self.get_object()
        if request.method == 'GET':
            serializer = CAPACommentSerializer(capa.comments.all(), many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            try:
                comment_obj = CAPAComment.objects.create(
                    capa=capa, comment=request.data.get('comment', ''),
                    author=request.user, phase=request.data.get('phase', None)
                )
                return Response(CAPACommentSerializer(comment_obj).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def capa_stats(self, request):
        """Dashboard statistics for CAPA overview."""
        queryset = self.get_queryset()
        now = timezone.now()
        today = now.date()

        # Count closed CAPAs
        closed_capas = queryset.filter(current_phase='closure')

        # Calculate average days to close
        closed_with_dates = closed_capas.filter(created_at__isnull=False, closed_date__isnull=False)
        if closed_with_dates.exists():
            total_days = sum(
                (c.closed_date.date() - c.created_at.date()).days
                for c in closed_with_dates
            )
            avg_days_to_close = total_days // closed_with_dates.count() if closed_with_dates.count() > 0 else 0
        else:
            avg_days_to_close = 0

        # Calculate effectiveness rate
        effective_capas = closed_capas.filter(
            effectiveness_result__in=['effective', 'partially_effective']
        ).count()
        effectiveness_rate = (effective_capas / closed_with_dates.count() * 100) if closed_with_dates.count() > 0 else 0

        stats = {
            'total_capas': queryset.count(),
            'open_capas': queryset.exclude(current_phase='closure').count(),
            'closed_capas': closed_capas.count(),
            'overdue_capas': queryset.filter(
                target_completion_date__lt=today,
                current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan', 'implementation', 'effectiveness']
            ).count(),
            'avg_days_to_close': avg_days_to_close,
            'effectiveness_rate': round(effectiveness_rate, 2),
            'by_phase': dict(
                queryset.values('current_phase').annotate(count=Count('id')).values_list('current_phase', 'count')
            ),
            'by_priority': dict(
                queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')
            ),
            'by_source': dict(
                queryset.values('source').annotate(count=Count('id')).values_list('source', 'count')
            ),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """List CAPAs past target_completion_date that aren't closed."""
        queryset = self.get_queryset()
        overdue_capas = queryset.filter(
            target_completion_date__lt=timezone.now().date(),
            current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan', 'implementation', 'effectiveness']
        ).order_by('target_completion_date')

        serializer = CAPAListSerializer(overdue_capas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Full activity timeline combining comments, transitions, approvals, documents."""
        capa = self.get_object()

        # Collect all timeline events
        timeline_events = []

        # Add phase transition events (use phase_entered_at as surrogate)
        timeline_events.append({
            'type': 'phase_transition',
            'timestamp': capa.phase_entered_at or capa.created_at,
            'description': f'Entered {capa.get_current_phase_display()} phase',
            'actor': capa.updated_by.username if capa.updated_by else 'System',
        })

        # Add comments with replies
        for comment in capa.comments.all():
            timeline_events.append({
                'type': 'comment',
                'timestamp': comment.created_at,
                'description': comment.comment,
                'actor': comment.author.username if comment.author else 'Unknown',
                'phase': comment.phase,
            })

        # Add document uploads
        for document in capa.documents.all():
            timeline_events.append({
                'type': 'document',
                'timestamp': document.uploaded_at,
                'description': f'Uploaded: {document.title}',
                'actor': document.uploaded_by.username if document.uploaded_by else 'Unknown',
                'phase': document.phase,
            })

        # Add approval responses
        for approval in capa.approvals.all():
            if approval.responded_at:
                timeline_events.append({
                    'type': 'approval',
                    'timestamp': approval.responded_at,
                    'description': f'{approval.get_approval_tier_display()} - {approval.get_status_display()}',
                    'actor': approval.approver.username if approval.approver else 'Unknown',
                    'phase': approval.phase,
                })

        # Add closure event
        if capa.current_phase == 'closure' and capa.closed_date:
            timeline_events.append({
                'type': 'closure',
                'timestamp': capa.closed_date,
                'description': f'CAPA Closed - {capa.effectiveness_result}',
                'actor': capa.closed_by.username if capa.closed_by else 'System',
            })

        # Sort by timestamp (newest first)
        timeline_events.sort(key=lambda x: x['timestamp'], reverse=True)

        return Response(timeline_events)


class CAPAApprovalViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet for CAPA approvals with create and read operations."""
    queryset = CAPAApproval.objects.select_related('capa', 'approver').all()
    serializer_class = CAPAApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['capa', 'status', 'phase']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        approval = self.get_object()
        serializer = ApprovalResponseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                approval.status = serializer.validated_data['status']
                approval.approver = request.user
                approval.comments = serializer.validated_data.get('comments', '')
                approval.save()
                return Response(CAPAApprovalSerializer(approval).data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
