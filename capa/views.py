from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

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


class CAPAViewSet(viewsets.ModelViewSet):
    """ViewSet for managing CAPAs with full lifecycle management."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['current_phase', 'priority', 'category', 'capa_type', 'source']
    search_fields = ['capa_id', 'title', 'description']
    ordering_fields = ['created_at', 'capa_id', 'title', 'priority']
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
        capa = self.get_object()
        serializer = PhaseTransitionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                capa.current_phase = serializer.validated_data['new_phase']
                capa.updated_by = request.user
                capa.save()
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
        capa = self.get_object()
        if request.method == 'GET':
            serializer = CAPADocumentSerializer(capa.documents.all(), many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            try:
                document = CAPADocument.objects.create(
                    capa=capa, file=request.FILES.get('file'),
                    document_type=request.data.get('document_type', ''),
                    title=request.data.get('title', ''), uploaded_by=request.user
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
    def dashboard_trends(self, request):
        from django.db.models import Count
        from django.utils import timezone
        queryset = self.get_queryset()
        stats = {
            'total_capas': queryset.count(),
            'by_phase': dict(queryset.values('current_phase').annotate(count=Count('id')).values_list('current_phase', 'count')),
            'by_priority': dict(queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'by_category': dict(queryset.values('category').annotate(count=Count('id')).values_list('category', 'count')),
            'overdue': queryset.filter(target_completion_date__lt=timezone.now().date(), current_phase__in=['investigation', 'root_cause', 'capa_plan', 'implementation']).count(),
        }
        return Response(stats)


class CAPAApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for CAPA approvals with respond action."""
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
