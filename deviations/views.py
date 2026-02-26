from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import FilterSet, CharFilter, DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count
from .models import Deviation, DeviationAttachment, DeviationComment
from .serializers import (
    DeviationListSerializer, DeviationDetailSerializer,
    DeviationCreateSerializer,
    DeviationAttachmentSerializer, DeviationCommentSerializer,
    StageTransitionSerializer
)


class DeviationFilterSet(FilterSet):
    """FilterSet for Deviation model with comprehensive filtering"""
    search = CharFilter(
        method='filter_search',
        label='Search deviations by ID, title, or description'
    )
    created_at_range = DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Deviation
        fields = [
            'current_stage', 'severity', 'category', 'deviation_type',
            'source', 'department', 'disposition'
        ]

    def filter_search(self, queryset, name, value):
        """Search across deviation_id, title, and description"""
        return queryset.filter(
            Q(deviation_id__icontains=value) |
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )


class DeviationViewSet(viewsets.ModelViewSet):
    """ViewSet for deviations with list/detail serializer pattern"""
    queryset = Deviation.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DeviationFilterSet
    search_fields = ['deviation_id', 'title', 'description']
    ordering_fields = ['created_at', 'severity', 'current_stage', 'target_closure_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return DeviationCreateSerializer
        elif self.action == 'retrieve':
            return DeviationDetailSerializer
        return DeviationListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def stage_transition(self, request, pk=None):
        """Move deviation through workflow stages with gate validation"""
        deviation = self.get_object()
        serializer = StageTransitionSerializer(data=request.data, context={'instance': deviation})

        if serializer.is_valid():
            try:
                target_stage = serializer.validated_data.get('target_stage')
                comments = serializer.validated_data.get('comments', '')

                # Gate validation: ensure required fields are filled before transition
                if deviation.current_stage == Deviation.STAGE_INVESTIGATION:
                    if not deviation.impact_assessment:
                        return Response(
                            {'error': 'Cannot leave investigation stage without impact assessment filled'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                if deviation.current_stage == Deviation.STAGE_CAPA_PLAN:
                    if not deviation.capa and not deviation.disposition_justification:
                        return Response(
                            {'error': 'Cannot leave CAPA plan stage without linked CAPA or justification'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Update stage
                deviation.current_stage = target_stage
                deviation.stage_entered_at = timezone.now()
                deviation.updated_by = request.user

                # Set closure date if moving to completed
                if target_stage == Deviation.STAGE_COMPLETED:
                    deviation.actual_closure_date = timezone.now()

                deviation.save()

                # Add comment about stage transition
                if comments:
                    DeviationComment.objects.create(
                        deviation=deviation,
                        author=request.user,
                        comment=f"Stage transitioned to {target_stage}: {comments}"
                    )

                return Response(
                    DeviationDetailSerializer(deviation).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def attachments(self, request, pk=None):
        """Get or upload attachments for a deviation"""
        deviation = self.get_object()

        if request.method == 'GET':
            attachments = DeviationAttachment.objects.filter(deviation=deviation)
            serializer = DeviationAttachmentSerializer(attachments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = DeviationAttachmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    deviation=deviation,
                    uploaded_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or add comments to a deviation"""
        deviation = self.get_object()

        if request.method == 'GET':
            comments = DeviationComment.objects.filter(deviation=deviation).order_by('-created_at')
            serializer = DeviationCommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = DeviationCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    deviation=deviation,
                    author=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """Get audit trail for a deviation"""
        deviation = self.get_object()

        audit_data = {
            'deviation_id': deviation.id,
            'created_by': deviation.created_by.username if deviation.created_by else None,
            'created_at': deviation.created_at,
            'updated_by': deviation.updated_by.username if deviation.updated_by else None,
            'updated_at': deviation.updated_at,
            'current_stage': deviation.current_stage,
            'severity': deviation.severity,
        }

        return Response(audit_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def deviation_stats(self, request):
        """Get deviation statistics across stages, severity, categories, sources, dispositions"""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_stage': dict(
                queryset.values('current_stage').annotate(count=Count('id')).values_list('current_stage', 'count')
            ),
            'by_severity': dict(
                queryset.values('severity').annotate(count=Count('id')).values_list('severity', 'count')
            ),
            'by_category': dict(
                queryset.values('category').annotate(count=Count('id')).values_list('category', 'count')
            ),
            'by_source': dict(
                queryset.values('source').annotate(count=Count('id')).values_list('source', 'count')
            ),
            'by_disposition': dict(
                queryset.values('disposition').annotate(count=Count('id')).values_list('disposition', 'count')
            ),
            'overdue_count': queryset.filter(
                target_closure_date__lt=timezone.now(),
                current_stage__in=[
                    Deviation.STAGE_OPENED,
                    Deviation.STAGE_QA_REVIEW,
                    Deviation.STAGE_INVESTIGATION,
                    Deviation.STAGE_CAPA_PLAN,
                ]
            ).count(),
        }

        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue deviations (past due_date and not completed)"""
        overdue_deviations = self.get_queryset().filter(
            target_closure_date__lt=timezone.now(),
            current_stage__in=[
                Deviation.STAGE_OPENED,
                Deviation.STAGE_QA_REVIEW,
                Deviation.STAGE_INVESTIGATION,
                Deviation.STAGE_CAPA_PLAN,
                Deviation.STAGE_PENDING_CAPA_APPROVAL,
                Deviation.STAGE_PENDING_CAPA_COMPLETION,
                Deviation.STAGE_PENDING_FINAL_APPROVAL,
            ]
        ).order_by('target_closure_date')

        serializer = DeviationListSerializer(overdue_deviations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def auto_create_capa(self, request, pk=None):
        """Create a linked CAPA from a deviation"""
        deviation = self.get_object()

        if deviation.capa:
            return Response(
                {'error': 'Deviation already has a linked CAPA'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from capa.models import CAPA
            capa = CAPA.objects.create(
                title=f"CAPA for {deviation.deviation_id}: {deviation.title}",
                description=f"Auto-created from deviation {deviation.deviation_id}",
                initiated_from_deviation=deviation,
                status='planning',
                created_by=request.user,
                updated_by=request.user
            )
            deviation.capa = capa
            deviation.requires_capa = True
            deviation.save()

            return Response(
                {'success': True, 'capa_id': capa.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get combined activity timeline including comments and transitions"""
        deviation = self.get_object()

        # Collect all timeline events
        events = []

        # Add comments
        comments = DeviationComment.objects.filter(deviation=deviation, parent__isnull=True).order_by('created_at')
        for comment in comments:
            events.append({
                'type': 'comment',
                'timestamp': comment.created_at,
                'author': comment.author.get_full_name(),
                'content': comment.comment,
                'stage': comment.stage
            })

        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])

        return Response(events, status=status.HTTP_200_OK)
