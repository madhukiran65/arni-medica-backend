from django.db.models import Q, Count
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    ValidationPlan,
    ValidationProtocol,
    ValidationTestCase,
    RTMEntry,
    ValidationDeviation,
    ValidationSummaryReport,
)
from .serializers import (
    ValidationPlanListSerializer,
    ValidationPlanDetailSerializer,
    ValidationProtocolListSerializer,
    ValidationProtocolDetailSerializer,
    ValidationTestCaseListSerializer,
    ValidationTestCaseDetailSerializer,
    RTMEntryListSerializer,
    RTMEntryDetailSerializer,
    ValidationDeviationListSerializer,
    ValidationDeviationDetailSerializer,
    ValidationSummaryReportListSerializer,
    ValidationSummaryReportDetailSerializer,
)


# FilterSets

class ValidationPlanFilterSet(filters.FilterSet):
    """FilterSet for ValidationPlan"""
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    system_name = filters.CharFilter(field_name='system_name', lookup_expr='icontains')
    status = filters.ChoiceFilter(
        field_name='status',
        choices=ValidationPlan.STATUS_CHOICES
    )
    validation_approach = filters.ChoiceFilter(
        field_name='validation_approach',
        choices=ValidationPlan.VALIDATION_APPROACH_CHOICES
    )
    responsible_person = filters.NumberFilter(field_name='responsible_person__id')
    qa_reviewer = filters.NumberFilter(field_name='qa_reviewer__id')
    department = filters.NumberFilter(field_name='department__id')
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = ValidationPlan
        fields = [
            'title',
            'system_name',
            'status',
            'validation_approach',
            'responsible_person',
            'qa_reviewer',
            'department',
            'created_after',
            'created_before',
        ]


class ValidationProtocolFilterSet(filters.FilterSet):
    """FilterSet for ValidationProtocol"""
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    protocol_type = filters.ChoiceFilter(
        field_name='protocol_type',
        choices=ValidationProtocol.PROTOCOL_TYPE_CHOICES
    )
    status = filters.ChoiceFilter(
        field_name='status',
        choices=ValidationProtocol.STATUS_CHOICES
    )
    result = filters.ChoiceFilter(
        field_name='result',
        choices=ValidationProtocol.RESULT_CHOICES
    )
    plan = filters.NumberFilter(field_name='plan__id')
    executed_by = filters.NumberFilter(field_name='executed_by__id')
    reviewed_by = filters.NumberFilter(field_name='reviewed_by__id')
    execution_after = filters.DateFilter(
        field_name='execution_date',
        lookup_expr='gte'
    )
    execution_before = filters.DateFilter(
        field_name='execution_date',
        lookup_expr='lte'
    )

    class Meta:
        model = ValidationProtocol
        fields = [
            'title',
            'protocol_type',
            'status',
            'result',
            'plan',
            'executed_by',
            'reviewed_by',
            'execution_after',
            'execution_before',
        ]


class ValidationTestCaseFilterSet(filters.FilterSet):
    """FilterSet for ValidationTestCase"""
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    test_type = filters.ChoiceFilter(
        field_name='test_type',
        choices=ValidationTestCase.TEST_TYPE_CHOICES
    )
    status = filters.ChoiceFilter(
        field_name='status',
        choices=ValidationTestCase.STATUS_CHOICES
    )
    priority = filters.ChoiceFilter(
        field_name='priority',
        choices=ValidationTestCase.PRIORITY_CHOICES
    )
    protocol = filters.NumberFilter(field_name='protocol__id')
    executed_by = filters.NumberFilter(field_name='executed_by__id')
    execution_after = filters.DateTimeFilter(
        field_name='execution_date',
        lookup_expr='gte'
    )
    execution_before = filters.DateTimeFilter(
        field_name='execution_date',
        lookup_expr='lte'
    )

    class Meta:
        model = ValidationTestCase
        fields = [
            'title',
            'test_type',
            'status',
            'priority',
            'protocol',
            'executed_by',
            'execution_after',
            'execution_before',
        ]


class RTMEntryFilterSet(filters.FilterSet):
    """FilterSet for RTMEntry"""
    requirement_id = filters.CharFilter(field_name='requirement_id', lookup_expr='icontains')
    requirement_category = filters.ChoiceFilter(
        field_name='requirement_category',
        choices=RTMEntry.REQUIREMENT_CATEGORY_CHOICES
    )
    verification_status = filters.ChoiceFilter(
        field_name='verification_status',
        choices=RTMEntry.VERIFICATION_STATUS_CHOICES
    )
    plan = filters.NumberFilter(field_name='plan__id')
    linked_protocol = filters.NumberFilter(field_name='linked_protocol__id')

    class Meta:
        model = RTMEntry
        fields = [
            'requirement_id',
            'requirement_category',
            'verification_status',
            'plan',
            'linked_protocol',
        ]


class ValidationDeviationFilterSet(filters.FilterSet):
    """FilterSet for ValidationDeviation"""
    severity = filters.ChoiceFilter(
        field_name='severity',
        choices=ValidationDeviation.SEVERITY_CHOICES
    )
    status = filters.ChoiceFilter(
        field_name='status',
        choices=ValidationDeviation.STATUS_CHOICES
    )
    resolution_type = filters.ChoiceFilter(
        field_name='resolution_type',
        choices=ValidationDeviation.RESOLUTION_TYPE_CHOICES
    )
    protocol = filters.NumberFilter(field_name='protocol__id')
    test_case = filters.NumberFilter(field_name='test_case__id')
    resolved_by = filters.NumberFilter(field_name='resolved_by__id')
    resolution_after = filters.DateTimeFilter(
        field_name='resolution_date',
        lookup_expr='gte'
    )
    resolution_before = filters.DateTimeFilter(
        field_name='resolution_date',
        lookup_expr='lte'
    )

    class Meta:
        model = ValidationDeviation
        fields = [
            'severity',
            'status',
            'resolution_type',
            'protocol',
            'test_case',
            'resolved_by',
            'resolution_after',
            'resolution_before',
        ]


class ValidationSummaryReportFilterSet(filters.FilterSet):
    """FilterSet for ValidationSummaryReport"""
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    overall_conclusion = filters.ChoiceFilter(
        field_name='overall_conclusion',
        choices=ValidationSummaryReport.CONCLUSION_CHOICES
    )
    status = filters.ChoiceFilter(
        field_name='status',
        choices=ValidationSummaryReport.REPORT_STATUS_CHOICES
    )
    plan = filters.NumberFilter(field_name='plan__id')
    approved_by = filters.NumberFilter(field_name='approved_by__id')
    approval_after = filters.DateTimeFilter(
        field_name='approval_date',
        lookup_expr='gte'
    )
    approval_before = filters.DateTimeFilter(
        field_name='approval_date',
        lookup_expr='lte'
    )

    class Meta:
        model = ValidationSummaryReport
        fields = [
            'title',
            'overall_conclusion',
            'status',
            'plan',
            'approved_by',
            'approval_after',
            'approval_before',
        ]


# ViewSets

class ValidationPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for ValidationPlan"""
    queryset = ValidationPlan.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ValidationPlanFilterSet
    filter_backends = [filters.DjangoFilterBackend]
    ordering_fields = ['created_at', 'updated_at', 'plan_id', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ValidationPlanDetailSerializer
        return ValidationPlanListSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a validation plan"""
        plan = self.get_object()
        if plan.status != 'draft':
            return Response(
                {'error': 'Only draft plans can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        plan.status = 'approved'
        plan.approval_date = timezone.now()
        plan.qa_reviewer = request.user
        plan.save()
        serializer = self.get_serializer(plan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_execution(self, request, pk=None):
        """Start execution of a validation plan"""
        plan = self.get_object()
        if plan.status not in ['approved', 'in_execution']:
            return Response(
                {'error': 'Plan must be approved to start execution'},
                status=status.HTTP_400_BAD_REQUEST
            )
        plan.status = 'in_execution'
        plan.save()
        serializer = self.get_serializer(plan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a validation plan"""
        plan = self.get_object()
        plan.status = 'completed'
        plan.save()
        serializer = self.get_serializer(plan)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get summary statistics for a validation plan"""
        plan = self.get_object()
        protocols = plan.protocols.all()
        test_cases = ValidationTestCase.objects.filter(protocol__plan=plan)
        deviations = ValidationDeviation.objects.filter(protocol__plan=plan)

        summary_data = {
            'plan_id': plan.plan_id,
            'title': plan.title,
            'status': plan.status,
            'protocol_count': protocols.count(),
            'protocols_approved': protocols.filter(status='approved').count(),
            'protocols_completed': protocols.filter(status='completed').count(),
            'test_case_count': test_cases.count(),
            'test_cases_passed': test_cases.filter(status='pass').count(),
            'test_cases_failed': test_cases.filter(status='fail').count(),
            'deviation_count': deviations.count(),
            'open_deviations': deviations.filter(status='open').count(),
            'rtm_entries': plan.rtm_entries.count(),
            'verified_requirements': plan.rtm_entries.filter(
                verification_status='verified'
            ).count(),
        }
        return Response(summary_data)


class ValidationProtocolViewSet(viewsets.ModelViewSet):
    """ViewSet for ValidationProtocol"""
    queryset = ValidationProtocol.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ValidationProtocolFilterSet
    filter_backends = [filters.DjangoFilterBackend]
    ordering_fields = ['created_at', 'updated_at', 'protocol_id', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ValidationProtocolDetailSerializer
        return ValidationProtocolListSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a validation protocol"""
        protocol = self.get_object()
        if protocol.status != 'draft':
            return Response(
                {'error': 'Only draft protocols can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        protocol.status = 'approved'
        protocol.approved_by = request.user
        protocol.save()
        serializer = self.get_serializer(protocol)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_execution(self, request, pk=None):
        """Start execution of a protocol"""
        protocol = self.get_object()
        if protocol.status not in ['approved', 'in_execution']:
            return Response(
                {'error': 'Protocol must be approved to start execution'},
                status=status.HTTP_400_BAD_REQUEST
            )
        protocol.status = 'in_execution'
        protocol.executed_by = request.user
        protocol.save()
        serializer = self.get_serializer(protocol)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_execution(self, request, pk=None):
        """Complete protocol execution"""
        protocol = self.get_object()
        result = request.data.get('result')
        result_summary = request.data.get('result_summary', '')

        if result not in dict(ValidationProtocol.RESULT_CHOICES):
            return Response(
                {'error': 'Invalid result status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        protocol.status = 'completed'
        protocol.result = result
        protocol.result_summary = result_summary
        protocol.execution_date = timezone.now()
        protocol.reviewed_by = request.user
        protocol.save()
        serializer = self.get_serializer(protocol)
        return Response(serializer.data)


class ValidationTestCaseViewSet(viewsets.ModelViewSet):
    """ViewSet for ValidationTestCase"""
    queryset = ValidationTestCase.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ValidationTestCaseFilterSet
    filter_backends = [filters.DjangoFilterBackend]
    ordering_fields = ['created_at', 'updated_at', 'test_case_id', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ValidationTestCaseDetailSerializer
        return ValidationTestCaseListSerializer

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a test case"""
        test_case = self.get_object()
        status_value = request.data.get('status')
        actual_result = request.data.get('actual_result', '')

        if status_value not in dict(ValidationTestCase.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        test_case.status = status_value
        test_case.actual_result = actual_result
        test_case.executed_by = request.user
        test_case.execution_date = timezone.now()
        test_case.save()
        serializer = self.get_serializer(test_case)
        return Response(serializer.data)


class RTMEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for RTMEntry"""
    queryset = RTMEntry.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = RTMEntryFilterSet
    filter_backends = [filters.DjangoFilterBackend]
    ordering_fields = ['created_at', 'updated_at', 'rtm_id']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RTMEntryDetailSerializer
        return RTMEntryListSerializer

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Mark an RTM entry as verified"""
        rtm = self.get_object()
        verification_status = request.data.get('verification_status')

        if verification_status not in dict(RTMEntry.VERIFICATION_STATUS_CHOICES):
            return Response(
                {'error': 'Invalid verification status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rtm.verification_status = verification_status
        rtm.save()
        serializer = self.get_serializer(rtm)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def verification_summary(self, request):
        """Get verification summary for all RTM entries"""
        plan_id = request.query_params.get('plan_id')

        if not plan_id:
            return Response(
                {'error': 'plan_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rtm_entries = RTMEntry.objects.filter(plan__id=plan_id)
        summary = {
            'total_requirements': rtm_entries.count(),
            'verified': rtm_entries.filter(
                verification_status='verified'
            ).count(),
            'not_verified': rtm_entries.filter(
                verification_status='not_verified'
            ).count(),
            'partially_verified': rtm_entries.filter(
                verification_status='partially_verified'
            ).count(),
            'failed': rtm_entries.filter(verification_status='failed').count(),
            'verification_percentage': round(
                (rtm_entries.filter(
                    verification_status='verified'
                ).count() / max(rtm_entries.count(), 1)) * 100, 2
            ),
        }
        return Response(summary)


class ValidationDeviationViewSet(viewsets.ModelViewSet):
    """ViewSet for ValidationDeviation"""
    queryset = ValidationDeviation.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ValidationDeviationFilterSet
    filter_backends = [filters.DjangoFilterBackend]
    ordering_fields = ['created_at', 'updated_at', 'deviation_id', 'severity']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ValidationDeviationDetailSerializer
        return ValidationDeviationListSerializer

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a deviation"""
        deviation = self.get_object()
        resolution = request.data.get('resolution')
        resolution_type = request.data.get('resolution_type')

        if resolution_type not in dict(ValidationDeviation.RESOLUTION_TYPE_CHOICES):
            return Response(
                {'error': 'Invalid resolution type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deviation.status = 'resolved'
        deviation.resolution = resolution
        deviation.resolution_type = resolution_type
        deviation.resolved_by = request.user
        deviation.resolution_date = timezone.now()
        deviation.save()
        serializer = self.get_serializer(deviation)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary_by_severity(self, request):
        """Get deviation summary grouped by severity"""
        plan_id = request.query_params.get('plan_id')
        protocol_id = request.query_params.get('protocol_id')

        deviations = ValidationDeviation.objects.all()

        if plan_id:
            deviations = deviations.filter(protocol__plan__id=plan_id)
        elif protocol_id:
            deviations = deviations.filter(protocol__id=protocol_id)

        summary = {
            severity[0]: deviations.filter(severity=severity[0]).count()
            for severity in ValidationDeviation.SEVERITY_CHOICES
        }
        summary['total'] = deviations.count()
        summary['open'] = deviations.filter(status='open').count()
        summary['resolved'] = deviations.filter(status='resolved').count()

        return Response(summary)


class ValidationSummaryReportViewSet(viewsets.ModelViewSet):
    """ViewSet for ValidationSummaryReport"""
    queryset = ValidationSummaryReport.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_class = ValidationSummaryReportFilterSet
    filter_backends = [filters.DjangoFilterBackend]
    ordering_fields = ['created_at', 'updated_at', 'report_id', 'overall_conclusion']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ValidationSummaryReportDetailSerializer
        return ValidationSummaryReportListSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a validation summary report"""
        report = self.get_object()
        if report.status != 'draft':
            return Response(
                {'error': 'Only draft reports can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report.status = 'approved'
        report.approved_by = request.user
        report.approval_date = timezone.now()
        report.save()
        serializer = self.get_serializer(report)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def move_to_review(self, request, pk=None):
        """Move a report to review status"""
        report = self.get_object()
        if report.status != 'draft':
            return Response(
                {'error': 'Only draft reports can be moved to review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report.status = 'in_review'
        report.save()
        serializer = self.get_serializer(report)
        return Response(serializer.data)
