from rest_framework import serializers
from .models import (
    ValidationPlan,
    ValidationProtocol,
    ValidationTestCase,
    RTMEntry,
    ValidationDeviation,
    ValidationSummaryReport,
)


class ValidationPlanListSerializer(serializers.ModelSerializer):
    """List view serializer for ValidationPlan"""
    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True
    )
    qa_reviewer_name = serializers.CharField(
        source='qa_reviewer.get_full_name',
        read_only=True,
        allow_null=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationPlan
        fields = [
            'id',
            'plan_id',
            'title',
            'system_name',
            'system_version',
            'validation_approach',
            'status',
            'responsible_person',
            'responsible_person_name',
            'qa_reviewer',
            'qa_reviewer_name',
            'department',
            'department_name',
            'approval_date',
            'target_completion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['plan_id', 'created_at', 'updated_at']


class ValidationPlanDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for ValidationPlan"""
    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True
    )
    qa_reviewer_name = serializers.CharField(
        source='qa_reviewer.get_full_name',
        read_only=True,
        allow_null=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        allow_null=True
    )
    protocol_count = serializers.SerializerMethodField()
    rtm_entry_count = serializers.SerializerMethodField()

    class Meta:
        model = ValidationPlan
        fields = [
            'id',
            'plan_id',
            'title',
            'system_name',
            'system_version',
            'description',
            'scope',
            'risk_assessment_summary',
            'validation_approach',
            'status',
            'responsible_person',
            'responsible_person_name',
            'qa_reviewer',
            'qa_reviewer_name',
            'department',
            'department_name',
            'approval_date',
            'target_completion',
            'protocol_count',
            'rtm_entry_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['plan_id', 'created_at', 'updated_at']

    def get_protocol_count(self, obj):
        return obj.protocols.count()

    def get_rtm_entry_count(self, obj):
        return obj.rtm_entries.count()


class ValidationTestCaseListSerializer(serializers.ModelSerializer):
    """List view serializer for ValidationTestCase"""
    executed_by_name = serializers.CharField(
        source='executed_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationTestCase
        fields = [
            'id',
            'test_case_id',
            'title',
            'test_type',
            'status',
            'priority',
            'executed_by',
            'executed_by_name',
            'execution_date',
            'created_at',
        ]
        read_only_fields = ['test_case_id', 'created_at']


class ValidationTestCaseDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for ValidationTestCase"""
    executed_by_name = serializers.CharField(
        source='executed_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationTestCase
        fields = [
            'id',
            'test_case_id',
            'protocol',
            'title',
            'description',
            'test_type',
            'preconditions',
            'test_steps',
            'expected_result',
            'actual_result',
            'status',
            'priority',
            'executed_by',
            'executed_by_name',
            'execution_date',
            'evidence_file',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['test_case_id', 'created_at', 'updated_at']


class ValidationProtocolListSerializer(serializers.ModelSerializer):
    """List view serializer for ValidationProtocol"""
    executed_by_name = serializers.CharField(
        source='executed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    test_case_count = serializers.SerializerMethodField()

    class Meta:
        model = ValidationProtocol
        fields = [
            'id',
            'protocol_id',
            'plan',
            'title',
            'protocol_type',
            'status',
            'result',
            'total_test_cases',
            'passed_test_cases',
            'failed_test_cases',
            'test_case_count',
            'execution_date',
            'executed_by',
            'executed_by_name',
            'created_at',
        ]
        read_only_fields = ['protocol_id', 'created_at']

    def get_test_case_count(self, obj):
        return obj.test_cases.count()


class ValidationProtocolDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for ValidationProtocol"""
    test_cases = ValidationTestCaseListSerializer(many=True, read_only=True)
    executed_by_name = serializers.CharField(
        source='executed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationProtocol
        fields = [
            'id',
            'protocol_id',
            'plan',
            'title',
            'protocol_type',
            'description',
            'prerequisites',
            'test_environment',
            'test_cases',
            'total_test_cases',
            'passed_test_cases',
            'failed_test_cases',
            'status',
            'result',
            'result_summary',
            'deviations_noted',
            'execution_date',
            'executed_by',
            'executed_by_name',
            'reviewed_by',
            'reviewed_by_name',
            'approved_by',
            'approved_by_name',
            'protocol_file',
            'result_file',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['protocol_id', 'created_at', 'updated_at']


class RTMEntryListSerializer(serializers.ModelSerializer):
    """List view serializer for RTMEntry"""
    class Meta:
        model = RTMEntry
        fields = [
            'id',
            'rtm_id',
            'plan',
            'requirement_id',
            'requirement_category',
            'verification_status',
            'created_at',
        ]
        read_only_fields = ['rtm_id', 'created_at']


class RTMEntryDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for RTMEntry"""
    linked_test_cases = ValidationTestCaseListSerializer(many=True, read_only=True)

    class Meta:
        model = RTMEntry
        fields = [
            'id',
            'rtm_id',
            'plan',
            'requirement_id',
            'requirement_text',
            'requirement_source',
            'requirement_category',
            'linked_test_cases',
            'linked_protocol',
            'verification_status',
            'gap_description',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['rtm_id', 'created_at', 'updated_at']


class ValidationDeviationListSerializer(serializers.ModelSerializer):
    """List view serializer for ValidationDeviation"""
    resolved_by_name = serializers.CharField(
        source='resolved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationDeviation
        fields = [
            'id',
            'deviation_id',
            'protocol',
            'test_case',
            'severity',
            'status',
            'resolved_by',
            'resolved_by_name',
            'resolution_date',
            'created_at',
        ]
        read_only_fields = ['deviation_id', 'created_at']


class ValidationDeviationDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for ValidationDeviation"""
    resolved_by_name = serializers.CharField(
        source='resolved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationDeviation
        fields = [
            'id',
            'deviation_id',
            'protocol',
            'test_case',
            'description',
            'severity',
            'impact_assessment',
            'resolution',
            'resolution_type',
            'status',
            'resolved_by',
            'resolved_by_name',
            'resolution_date',
            'linked_deviation',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['deviation_id', 'created_at', 'updated_at']


class ValidationSummaryReportListSerializer(serializers.ModelSerializer):
    """List view serializer for ValidationSummaryReport"""
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationSummaryReport
        fields = [
            'id',
            'report_id',
            'plan',
            'title',
            'overall_conclusion',
            'status',
            'approved_by',
            'approved_by_name',
            'approval_date',
            'created_at',
        ]
        read_only_fields = ['report_id', 'created_at']


class ValidationSummaryReportDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for ValidationSummaryReport"""
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ValidationSummaryReport
        fields = [
            'id',
            'report_id',
            'plan',
            'title',
            'iq_status',
            'oq_status',
            'pq_status',
            'overall_test_count',
            'overall_pass_count',
            'overall_fail_count',
            'deviations_count',
            'open_deviations_count',
            'overall_conclusion',
            'executive_summary',
            'recommendations',
            'status',
            'approved_by',
            'approved_by_name',
            'approval_date',
            'linked_document',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['report_id', 'created_at', 'updated_at']
