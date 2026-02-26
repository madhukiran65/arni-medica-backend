from django.contrib import admin
from .models import (
    ValidationPlan,
    ValidationProtocol,
    ValidationTestCase,
    RTMEntry,
    ValidationDeviation,
    ValidationSummaryReport,
)


@admin.register(ValidationPlan)
class ValidationPlanAdmin(admin.ModelAdmin):
    list_display = [
        'plan_id',
        'title',
        'system_name',
        'status',
        'validation_approach',
        'responsible_person',
        'target_completion',
    ]
    list_filter = [
        'status',
        'validation_approach',
        'created_at',
        'updated_at',
        'department',
    ]
    search_fields = [
        'plan_id',
        'title',
        'system_name',
        'description',
    ]
    readonly_fields = [
        'plan_id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('plan_id', 'title', 'system_name', 'system_version')
        }),
        ('Description', {
            'fields': ('description', 'scope', 'risk_assessment_summary')
        }),
        ('Validation Configuration', {
            'fields': ('validation_approach', 'test_environment')
        }),
        ('Assignments', {
            'fields': ('responsible_person', 'qa_reviewer', 'department')
        }),
        ('Status and Dates', {
            'fields': ('status', 'approval_date', 'target_completion')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']


@admin.register(ValidationProtocol)
class ValidationProtocolAdmin(admin.ModelAdmin):
    list_display = [
        'protocol_id',
        'title',
        'protocol_type',
        'plan',
        'status',
        'result',
        'total_test_cases',
        'passed_test_cases',
    ]
    list_filter = [
        'protocol_type',
        'status',
        'result',
        'execution_date',
        'created_at',
    ]
    search_fields = [
        'protocol_id',
        'title',
        'description',
        'plan__title',
    ]
    readonly_fields = [
        'protocol_id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('protocol_id', 'plan', 'title', 'protocol_type')
        }),
        ('Description', {
            'fields': ('description', 'test_environment', 'prerequisites')
        }),
        ('Test Cases', {
            'fields': (
                'total_test_cases',
                'passed_test_cases',
                'failed_test_cases',
                'test_cases'
            )
        }),
        ('Execution', {
            'fields': (
                'status',
                'execution_date',
                'executed_by',
                'reviewed_by',
                'approved_by'
            )
        }),
        ('Results', {
            'fields': ('result', 'result_summary', 'deviations_noted')
        }),
        ('Files', {
            'fields': ('protocol_file', 'result_file')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']


@admin.register(ValidationTestCase)
class ValidationTestCaseAdmin(admin.ModelAdmin):
    list_display = [
        'test_case_id',
        'title',
        'protocol',
        'test_type',
        'priority',
        'status',
        'executed_by',
    ]
    list_filter = [
        'test_type',
        'priority',
        'status',
        'execution_date',
        'created_at',
    ]
    search_fields = [
        'test_case_id',
        'title',
        'description',
        'protocol__title',
    ]
    readonly_fields = [
        'test_case_id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('test_case_id', 'protocol', 'title')
        }),
        ('Description', {
            'fields': ('description', 'test_type', 'priority')
        }),
        ('Test Details', {
            'fields': (
                'preconditions',
                'test_steps',
                'expected_result',
                'actual_result'
            )
        }),
        ('Execution', {
            'fields': ('status', 'executed_by', 'execution_date')
        }),
        ('Evidence', {
            'fields': ('evidence_file', 'notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']


@admin.register(RTMEntry)
class RTMEntryAdmin(admin.ModelAdmin):
    list_display = [
        'rtm_id',
        'requirement_id',
        'plan',
        'requirement_category',
        'verification_status',
    ]
    list_filter = [
        'requirement_category',
        'verification_status',
        'created_at',
    ]
    search_fields = [
        'rtm_id',
        'requirement_id',
        'requirement_text',
        'plan__title',
    ]
    readonly_fields = [
        'rtm_id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('rtm_id', 'plan', 'requirement_id')
        }),
        ('Requirement Details', {
            'fields': (
                'requirement_text',
                'requirement_source',
                'requirement_category'
            )
        }),
        ('Verification', {
            'fields': (
                'linked_test_cases',
                'linked_protocol',
                'verification_status'
            )
        }),
        ('Notes', {
            'fields': ('gap_description', 'notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ['linked_test_cases']
    ordering = ['-created_at']


@admin.register(ValidationDeviation)
class ValidationDeviationAdmin(admin.ModelAdmin):
    list_display = [
        'deviation_id',
        'protocol',
        'severity',
        'status',
        'resolution_type',
        'resolved_by',
    ]
    list_filter = [
        'severity',
        'status',
        'resolution_type',
        'resolution_date',
        'created_at',
    ]
    search_fields = [
        'deviation_id',
        'description',
        'protocol__title',
    ]
    readonly_fields = [
        'deviation_id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('deviation_id', 'protocol', 'test_case')
        }),
        ('Description', {
            'fields': ('description', 'severity', 'impact_assessment')
        }),
        ('Resolution', {
            'fields': (
                'status',
                'resolution',
                'resolution_type',
                'resolved_by',
                'resolution_date'
            )
        }),
        ('Linking', {
            'fields': ('linked_deviation',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']


@admin.register(ValidationSummaryReport)
class ValidationSummaryReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_id',
        'title',
        'plan',
        'overall_conclusion',
        'status',
        'approved_by',
    ]
    list_filter = [
        'overall_conclusion',
        'status',
        'iq_status',
        'oq_status',
        'pq_status',
        'approval_date',
        'created_at',
    ]
    search_fields = [
        'report_id',
        'title',
        'executive_summary',
        'plan__title',
    ]
    readonly_fields = [
        'report_id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('report_id', 'plan', 'title')
        }),
        ('Qualification Status', {
            'fields': ('iq_status', 'oq_status', 'pq_status')
        }),
        ('Test Statistics', {
            'fields': (
                'overall_test_count',
                'overall_pass_count',
                'overall_fail_count'
            )
        }),
        ('Deviations', {
            'fields': ('deviations_count', 'open_deviations_count')
        }),
        ('Conclusion', {
            'fields': ('overall_conclusion', 'executive_summary', 'recommendations')
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approval_date')
        }),
        ('Linking', {
            'fields': ('linked_document',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']
