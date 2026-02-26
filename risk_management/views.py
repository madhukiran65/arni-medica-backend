from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    RiskCategory, Hazard, RiskAssessment, RiskMitigation,
    FMEAWorksheet, FMEARecord, RiskReport, RiskMonitoringAlert
)
from .serializers import (
    RiskCategoryListSerializer, RiskCategoryDetailSerializer,
    HazardListSerializer, HazardDetailSerializer,
    RiskAssessmentListSerializer, RiskAssessmentDetailSerializer,
    RiskMitigationListSerializer, RiskMitigationDetailSerializer,
    FMEAWorksheetListSerializer, FMEAWorksheetDetailSerializer,
    FMEARecordListSerializer, FMEARecordDetailSerializer,
    RiskReportListSerializer, RiskReportDetailSerializer,
    RiskMonitoringAlertListSerializer, RiskMonitoringAlertDetailSerializer
)


class RiskCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk Categories"""
    queryset = RiskCategory.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RiskCategoryDetailSerializer
        return RiskCategoryListSerializer


class HazardViewSet(viewsets.ModelViewSet):
    """ViewSet for Hazards"""
    queryset = Hazard.objects.select_related(
        'category', 'product_line', 'department',
        'linked_complaint', 'linked_deviation'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'category', 'product_line', 'department']
    search_fields = ['hazard_id', 'name', 'harm_description']
    ordering_fields = ['hazard_id', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HazardDetailSerializer
        return HazardListSerializer


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk Assessments"""
    queryset = RiskAssessment.objects.select_related('hazard', 'assessed_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assessment_type', 'acceptability', 'hazard']
    search_fields = ['hazard__hazard_id', 'hazard__name']
    ordering_fields = ['assessment_date', 'created_at']
    ordering = ['-assessment_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RiskAssessmentDetailSerializer
        return RiskAssessmentListSerializer

    def perform_create(self, serializer):
        serializer.save(assessed_by=self.request.user)


class RiskMitigationViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk Mitigations"""
    queryset = RiskMitigation.objects.select_related(
        'hazard', 'responsible_person', 'linked_change_control', 'linked_document'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['implementation_status', 'mitigation_type', 'hazard']
    search_fields = ['hazard__hazard_id', 'description']
    ordering_fields = ['target_date', 'implementation_status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RiskMitigationDetailSerializer
        return RiskMitigationListSerializer


class FMEAWorksheetViewSet(viewsets.ModelViewSet):
    """ViewSet for FMEA Worksheets"""
    queryset = FMEAWorksheet.objects.select_related(
        'product_line', 'approved_by'
    ).prefetch_related('records')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'fmea_type', 'product_line']
    search_fields = ['fmea_id', 'title', 'description']
    ordering_fields = ['fmea_id', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FMEAWorksheetDetailSerializer
        return FMEAWorksheetListSerializer


class FMEARecordViewSet(viewsets.ModelViewSet):
    """ViewSet for FMEA Records"""
    queryset = FMEARecord.objects.select_related(
        'worksheet', 'responsible_person'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['worksheet', 'responsible_person']
    search_fields = ['worksheet__fmea_id', 'failure_mode', 'failure_cause']
    ordering_fields = ['created_at', 'completion_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FMEARecordDetailSerializer
        return FMEARecordListSerializer


class RiskReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk Reports"""
    queryset = RiskReport.objects.select_related(
        'product_line', 'linked_document'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'report_type', 'overall_risk_acceptability', 'product_line']
    search_fields = ['report_id', 'title', 'description']
    ordering_fields = ['report_id', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RiskReportDetailSerializer
        return RiskReportListSerializer


class RiskMonitoringAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Risk Monitoring Alerts"""
    queryset = RiskMonitoringAlert.objects.select_related(
        'hazard', 'acknowledged_by'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'is_acknowledged', 'hazard']
    search_fields = ['hazard__hazard_id', 'message']
    ordering_fields = ['created_at', 'acknowledged_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RiskMonitoringAlertDetailSerializer
        return RiskMonitoringAlertListSerializer
