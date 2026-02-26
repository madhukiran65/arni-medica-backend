from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Complaint,
    ComplaintAttachment,
    MIRRecord,
    ComplaintComment,
    PMSPlan,
    TrendAnalysis,
    PMSReport,
    VigilanceReport,
    LiteratureReview,
    SafetySignal,
)
from .serializers import (
    ComplaintListSerializer,
    ComplaintDetailSerializer,
    ComplaintAttachmentSerializer,
    MIRRecordListSerializer,
    MIRRecordDetailSerializer,
    ComplaintCommentSerializer,
    PMSPlanListSerializer,
    PMSPlanDetailSerializer,
    TrendAnalysisListSerializer,
    TrendAnalysisDetailSerializer,
    PMSReportListSerializer,
    PMSReportDetailSerializer,
    VigilanceReportListSerializer,
    VigilanceReportDetailSerializer,
    LiteratureReviewListSerializer,
    LiteratureReviewDetailSerializer,
    SafetySignalListSerializer,
    SafetySignalDetailSerializer,
)
from .filters import (
    ComplaintFilterSet,
    PMSPlanFilterSet,
    TrendAnalysisFilterSet,
    PMSReportFilterSet,
    VigilanceReportFilterSet,
    LiteratureReviewFilterSet,
    SafetySignalFilterSet,
)


class ComplaintViewSet(viewsets.ModelViewSet):
    """ViewSet for Complaint"""

    queryset = Complaint.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ComplaintFilterSet
    search_fields = ['complaint_id', 'title', 'product_name', 'complainant_name']
    ordering_fields = ['received_date', 'complaint_id', 'status', 'severity']
    ordering = ['-received_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ComplaintDetailSerializer
        return ComplaintListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        """Assign complaint to a user"""
        complaint = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        if assigned_to_id:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=assigned_to_id)
                complaint.assigned_to = user
                complaint.updated_by = request.user
                complaint.save()
                return Response({'status': 'Complaint assigned'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'assigned_to_id required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_investigation(self, request, pk=None):
        """Start investigation of complaint"""
        complaint = self.get_object()
        if complaint.status == 'new':
            complaint.status = 'under_investigation'
            complaint.updated_by = request.user
            complaint.save()
            return Response({'status': 'Investigation started'}, status=status.HTTP_200_OK)
        return Response({'error': 'Only new complaints can start investigation'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete_investigation(self, request, pk=None):
        """Mark investigation as complete"""
        complaint = self.get_object()
        if complaint.status == 'under_investigation':
            complaint.status = 'investigation_complete'
            complaint.investigation_completed_date = request.data.get('investigation_completed_date')
            complaint.investigation_summary = request.data.get('investigation_summary', complaint.investigation_summary)
            complaint.root_cause = request.data.get('root_cause', complaint.root_cause)
            complaint.investigated_by = request.user
            complaint.updated_by = request.user
            complaint.save()
            return Response({'status': 'Investigation completed'}, status=status.HTTP_200_OK)
        return Response({'error': 'Complaint must be under investigation'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def determine_reportability(self, request, pk=None):
        """Determine FDA reportability"""
        complaint = self.get_object()
        complaint.is_reportable_to_fda = request.data.get('is_reportable_to_fda', False)
        complaint.reportability_justification = request.data.get('reportability_justification', '')
        complaint.reportability_determination_date = request.data.get('reportability_determination_date')
        complaint.reportability_determined_by = request.user
        complaint.updated_by = request.user
        complaint.save()
        return Response({'status': 'Reportability determined'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        """Close a complaint"""
        complaint = self.get_object()
        complaint.status = 'closed'
        complaint.actual_closure_date = request.data.get('actual_closure_date')
        complaint.resolution_description = request.data.get('resolution_description', complaint.resolution_description)
        complaint.closed_by = request.user
        complaint.updated_by = request.user
        complaint.save()
        return Response({'status': 'Complaint closed'}, status=status.HTTP_200_OK)


class ComplaintAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for ComplaintAttachment"""

    queryset = ComplaintAttachment.objects.all()
    serializer_class = ComplaintAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['complaint', 'attachment_type']
    search_fields = ['file_name', 'description']
    ordering = ['-uploaded_at']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class MIRRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for MIRRecord"""

    queryset = MIRRecord.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['complaint', 'report_type']
    search_fields = ['mir_number', 'narrative']
    ordering = ['-submitted_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MIRRecordDetailSerializer
        return MIRRecordListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ComplaintCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for ComplaintComment"""

    queryset = ComplaintComment.objects.all()
    serializer_class = ComplaintCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['complaint']
    ordering = ['created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ============================================================================
# PMS (Post-Market Surveillance) ViewSets - Merged from pms app
# ============================================================================


class PMSPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for PMSPlan"""

    queryset = PMSPlan.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PMSPlanFilterSet
    search_fields = ['plan_id', 'title', 'product_name', 'product_line__name']
    ordering_fields = ['created_at', 'plan_id', 'status', 'effective_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PMSPlanDetailSerializer
        return PMSPlanListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        """Activate a PMS Plan"""
        plan = self.get_object()
        if plan.status == 'draft':
            plan.status = 'active'
            plan.updated_by = request.user
            plan.save()
            return Response(
                {'status': 'Plan activated'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Only draft plans can be activated'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        """Close a PMS Plan"""
        plan = self.get_object()
        plan.status = 'closed'
        plan.updated_by = request.user
        plan.save()
        return Response(
            {'status': 'Plan closed'},
            status=status.HTTP_200_OK,
        )


class TrendAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for TrendAnalysis"""

    queryset = TrendAnalysis.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TrendAnalysisFilterSet
    search_fields = ['trend_id', 'pms_plan__title', 'analysis_summary']
    ordering_fields = ['created_at', 'trend_id', 'analysis_period_start', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrendAnalysisDetailSerializer
        return TrendAnalysisListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a trend analysis"""
        analysis = self.get_object()
        if analysis.status != 'approved':
            analysis.status = 'approved'
            analysis.updated_by = request.user
            analysis.save()
            return Response(
                {'status': 'Analysis approved'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Analysis already approved'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def request_action(self, request, pk=None):
        """Mark analysis as requiring action"""
        analysis = self.get_object()
        analysis.status = 'action_required'
        analysis.updated_by = request.user
        analysis.save()
        return Response(
            {'status': 'Action required marked'},
            status=status.HTTP_200_OK,
        )


class PMSReportViewSet(viewsets.ModelViewSet):
    """ViewSet for PMSReport"""

    queryset = PMSReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PMSReportFilterSet
    search_fields = ['report_id', 'title', 'pms_plan__title']
    ordering_fields = ['created_at', 'report_id', 'period_start', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PMSReportDetailSerializer
        return PMSReportListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """Submit a PMS Report"""
        report = self.get_object()
        if report.status == 'approved':
            report.status = 'submitted'
            report.updated_by = request.user
            report.save()
            return Response(
                {'status': 'Report submitted'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Only approved reports can be submitted'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a PMS Report"""
        report = self.get_object()
        if report.status == 'in_review':
            report.status = 'approved'
            report.approved_by = request.user
            report.updated_by = request.user
            report.save()
            return Response(
                {'status': 'Report approved'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Only reports in review can be approved'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VigilanceReportViewSet(viewsets.ModelViewSet):
    """ViewSet for VigilanceReport"""

    queryset = VigilanceReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VigilanceReportFilterSet
    search_fields = ['vigilance_id', 'complaint__complaint_id', 'tracking_number']
    ordering_fields = ['created_at', 'vigilance_id', 'submission_deadline', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VigilanceReportDetailSerializer
        return VigilanceReportListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """Submit a vigilance report"""
        report = self.get_object()
        if report.status == 'pending_submission':
            report.status = 'submitted'
            report.submitted_by = request.user
            report.actual_submission_date = request.data.get(
                'actual_submission_date',
                report.actual_submission_date,
            )
            report.updated_by = request.user
            report.save()
            return Response(
                {'status': 'Report submitted'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Only pending reports can be submitted'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def acknowledge_response(self, request, pk=None):
        """Acknowledge authority response"""
        report = self.get_object()
        report.status = 'acknowledged'
        report.response_date = request.data.get('response_date', report.response_date)
        report.authority_response = request.data.get(
            'authority_response',
            report.authority_response,
        )
        report.updated_by = request.user
        report.save()
        return Response(
            {'status': 'Response acknowledged'},
            status=status.HTTP_200_OK,
        )


class LiteratureReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for LiteratureReview"""

    queryset = LiteratureReview.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LiteratureReviewFilterSet
    search_fields = ['review_id', 'title', 'pms_plan__title']
    ordering_fields = ['created_at', 'review_id', 'search_date', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LiteratureReviewDetailSerializer
        return LiteratureReviewListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Complete a literature review"""
        review = self.get_object()
        if review.status == 'in_progress':
            review.status = 'completed'
            review.reviewed_by = request.user
            review.updated_by = request.user
            review.save()
            return Response(
                {'status': 'Review completed'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Only in-progress reviews can be completed'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def flag_action_required(self, request, pk=None):
        """Flag review as requiring action"""
        review = self.get_object()
        review.status = 'action_required'
        review.updated_by = request.user
        review.save()
        return Response(
            {'status': 'Flagged for action'},
            status=status.HTTP_200_OK,
        )


class SafetySignalViewSet(viewsets.ModelViewSet):
    """ViewSet for SafetySignal"""

    queryset = SafetySignal.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SafetySignalFilterSet
    search_fields = ['signal_id', 'title', 'description', 'product_line__name']
    ordering_fields = ['created_at', 'signal_id', 'detection_date', 'severity', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SafetySignalDetailSerializer
        return SafetySignalListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        """Confirm a safety signal"""
        signal = self.get_object()
        if signal.status == 'under_evaluation':
            signal.status = 'confirmed'
            signal.evaluated_by = request.user
            signal.updated_by = request.user
            signal.save()
            return Response(
                {'status': 'Signal confirmed'},
                status=status.HTTP_200_OK,
            )
        return Response(
            {'error': 'Only signals under evaluation can be confirmed'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def refute(self, request, pk=None):
        """Refute a safety signal"""
        signal = self.get_object()
        signal.status = 'refuted'
        signal.evaluation_summary = request.data.get(
            'evaluation_summary',
            signal.evaluation_summary,
        )
        signal.evaluated_by = request.user
        signal.updated_by = request.user
        signal.save()
        return Response(
            {'status': 'Signal refuted'},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        """Close a safety signal"""
        signal = self.get_object()
        signal.status = 'closed'
        signal.updated_by = request.user
        signal.save()
        return Response(
            {'status': 'Signal closed'},
            status=status.HTTP_200_OK,
        )
