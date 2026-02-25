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
    """
    ViewSet for managing CAPAs with full lifecycle management,
    approvals, supporting documents, and comments.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['current_phase', 'priority', 'category', 'capa_type', 'source', 'department']
    search_fields = ['capa_id', 'title', 'description']
    ordering_fields = ['created_at', 'capa_id', 'title', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Build queryset with optimized queries."""
        queryset = CAPA.objects.select_related(
            'department',
            'category',
            'capa_type',
            'source'
        ).prefetch_related(
            Prefetch('approvals', queryset=CAPAApproval.objects.select_related('approved_by')),
            Prefetch('documents', queryset=CAPADocument.objects.select_related('uploaded_by')),
            Prefetch('comments', queryset=CAPAComment.objects.select_related('created_by').order_by('-created_at'))
        ).all()
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
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
        """Set created_by to current user on creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def phase_transition(self, request, pk=None):
        """
        Transition CAPA to a new phase with gate validation.
        POST body: { "new_phase": "string", "reason": "string" }
        """
        capa = self.get_object()
        serializer = PhaseTransitionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                new_phase = serializer.validated_data['new_phase']
                capa.current_phase = new_phase
                capa.updated_by = request.user
                capa.save()
                return Response(
                    CAPADetailSerializer(capa).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_risk_matrix(self, request, pk=None):
        """
        Update risk scores (severity, likelihood, RPN).
        POST body: { "severity": int, "likelihood": int }
        """
        capa = self.get_object()
        serializer = RiskMatrixSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                capa.risk_severity = serializer.validated_data.get('severity')
                capa.risk_likelihood = serializer.validated_data.get('likelihood')
                capa.updated_by = request.user
                capa.save()
                return Response(
                    CAPADetailSerializer(capa).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'patch'])
    def update_five_w(self, request, pk=None):
        """
        Update 5W analysis (Why, What, When, Where, Who).
        POST/PATCH body: { "why": "string", "what": "string", "when": "string", "where": "string", "who": "string" }
        """
        capa = self.get_object()
        serializer = FiveWAnalysisSerializer(data=request.data, partial=True)
        
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                if 'why' in data:
                    capa.analysis_why = data['why']
                if 'what' in data:
                    capa.analysis_what = data['what']
                if 'when' in data:
                    capa.analysis_when = data['when']
                if 'where' in data:
                    capa.analysis_where = data['where']
                if 'who' in data:
                    capa.analysis_who = data['who']
                capa.updated_by = request.user
                capa.save()
                return Response(
                    CAPADetailSerializer(capa).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def request_extension(self, request, pk=None):
        """
        Request deadline extension.
        POST body: { "new_deadline": "date", "reason": "string" }
        """
        capa = self.get_object()
        serializer = ExtensionRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                capa.deadline = serializer.validated_data['new_deadline']
                capa.extension_reason = serializer.validated_data.get('reason', '')
                capa.updated_by = request.user
                capa.save()
                return Response(
                    CAPADetailSerializer(capa).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def approvals(self, request, pk=None):
        """List approvals for current phase."""
        capa = self.get_object()
        approvals = capa.approvals.filter(phase=capa.current_phase)
        serializer = CAPAApprovalSerializer(approvals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond_approval(self, request, pk=None):
        """
        Approve or reject CAPA.
        POST body: { "approval_id": int, "status": "approved|rejected", "signature": "string", "comment": "string" }
        """
        capa = self.get_object()
        serializer = ApprovalResponseSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                approval = CAPAApproval.objects.get(
                    id=serializer.validated_data['approval_id'],
                    capa=capa
                )
                approval.status = serializer.validated_data['status']
                approval.approved_by = request.user
                approval.signature = serializer.validated_data.get('signature', '')
                approval.comment = serializer.validated_data.get('comment', '')
                approval.save()
                
                return Response(
                    CAPAApprovalSerializer(approval).data,
                    status=status.HTTP_200_OK
                )
            except CAPAApproval.DoesNotExist:
                return Response(
                    {'error': 'Approval not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        """List or upload supporting documents."""
        capa = self.get_object()
        
        if request.method == 'GET':
            documents = capa.documents.all()
            serializer = CAPADocumentSerializer(documents, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            try:
                document = CAPADocument.objects.create(
                    capa=capa,
                    file=request.FILES.get('file'),
                    document_type=request.data.get('document_type', ''),
                    uploaded_by=request.user
                )
                return Response(
                    CAPADocumentSerializer(document).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """List or create comments."""
        capa = self.get_object()
        
        if request.method == 'GET':
            comments = capa.comments.all()
            serializer = CAPACommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            try:
                comment = CAPAComment.objects.create(
                    capa=capa,
                    text=request.data.get('text', ''),
                    created_by=request.user
                )
                return Response(
                    CAPACommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=False, methods=['get'])
    def dashboard_trends(self, request):
        """Get aggregate statistics for dashboard."""
        from django.db.models import Count, Q
        from django.utils import timezone
        
        queryset = self.get_queryset()
        
        stats = {
            'total_capas': queryset.count(),
            'by_phase': dict(queryset.values('current_phase').annotate(count=Count('id')).values_list('current_phase', 'count')),
            'by_priority': dict(queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'by_category': dict(queryset.values('category__name').annotate(count=Count('id')).values_list('category__name', 'count')),
            'overdue': queryset.filter(deadline__lt=timezone.now(), current_phase__in=['open', 'in_progress']).count(),
        }
        
        return Response(stats)


class CAPAApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for CAPA approvals with respond action.
    """
    queryset = CAPAApproval.objects.select_related(
        'capa',
        'approved_by'
    ).all()
    serializer_class = CAPAApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['capa', 'status', 'phase']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """
        Respond to an approval request.
        POST body: { "status": "approved|rejected", "signature": "string", "comment": "string" }
        """
        approval = self.get_object()
        serializer = ApprovalResponseSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                approval.status = serializer.validated_data['status']
                approval.approved_by = request.user
                approval.signature = serializer.validated_data.get('signature', '')
                approval.comment = serializer.validated_data.get('comment', '')
                approval.save()
                
                return Response(
                    CAPAApprovalSerializer(approval).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
