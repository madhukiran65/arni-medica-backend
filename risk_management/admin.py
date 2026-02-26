from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RiskCategory, Hazard, RiskAssessment, RiskMitigation,
    FMEAWorksheet, FMEARecord, RiskReport, RiskMonitoringAlert
)


@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Hazard)
class HazardAdmin(admin.ModelAdmin):
    list_display = ['hazard_id', 'name', 'source', 'status', 'category', 'severity_badge']
    list_filter = ['status', 'source', 'category', 'product_line', 'department', 'created_at']
    search_fields = ['hazard_id', 'name', 'harm_description']
    readonly_fields = ['hazard_id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Identification', {
            'fields': ('hazard_id', 'name', 'description', 'category')
        }),
        ('Hazard Details', {
            'fields': (
                'source', 'harm_description', 'affected_population',
                'severity_of_harm', 'status'
            )
        }),
        ('Relationships', {
            'fields': (
                'product_line', 'department', 'linked_complaint', 'linked_deviation'
            ),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def severity_badge(self, obj):
        severity_map = {
            'Catastrophic': '#d32f2f',
            'Major': '#f57c00',
            'Moderate': '#fbc02d',
            'Minor': '#388e3c',
        }
        color = severity_map.get(obj.severity_of_harm, '#9e9e9e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.severity_of_harm or 'Unknown'
        )
    severity_badge.short_description = 'Severity'


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['hazard', 'assessment_type', 'rpn_badge', 'risk_level_badge', 'acceptability']
    list_filter = ['assessment_type', 'acceptability', 'assessment_date']
    search_fields = ['hazard__hazard_id', 'hazard__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'rpn', 'risk_level']

    fieldsets = (
        ('Assessment', {
            'fields': ('hazard', 'assessment_type', 'acceptability')
        }),
        ('Scoring', {
            'fields': ('severity', 'occurrence', 'detection', 'rpn', 'risk_level')
        }),
        ('Justification', {
            'fields': ('justification',)
        }),
        ('Review', {
            'fields': ('assessed_by', 'assessment_date')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rpn_badge(self, obj):
        rpn = obj.rpn
        if rpn >= 100:
            color = '#d32f2f'
        elif rpn >= 50:
            color = '#f57c00'
        elif rpn >= 20:
            color = '#fbc02d'
        else:
            color = '#388e3c'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            rpn
        )
    rpn_badge.short_description = 'RPN'

    def risk_level_badge(self, obj):
        level_colors = {
            'critical': '#d32f2f',
            'high': '#f57c00',
            'medium': '#fbc02d',
            'low': '#388e3c',
        }
        level = obj.risk_level
        color = level_colors.get(level, '#9e9e9e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; text-transform: uppercase; font-weight: bold;">{}</span>',
            color,
            level
        )
    risk_level_badge.short_description = 'Risk Level'


@admin.register(RiskMitigation)
class RiskMitigationAdmin(admin.ModelAdmin):
    list_display = ['hazard', 'mitigation_type', 'implementation_status', 'target_date']
    list_filter = ['mitigation_type', 'implementation_status', 'target_date', 'created_at']
    search_fields = ['hazard__hazard_id', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Mitigation', {
            'fields': ('hazard', 'mitigation_type', 'description')
        }),
        ('Status and Schedule', {
            'fields': ('implementation_status', 'target_date', 'completion_date')
        }),
        ('Verification', {
            'fields': ('verification_method', 'verification_result')
        }),
        ('Responsibility', {
            'fields': ('responsible_person',)
        }),
        ('Linked Items', {
            'fields': ('linked_change_control', 'linked_document'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FMEAWorksheet)
class FMEAWorksheetAdmin(admin.ModelAdmin):
    list_display = ['fmea_id', 'title', 'fmea_type', 'status', 'product_line']
    list_filter = ['status', 'fmea_type', 'product_line', 'created_at']
    search_fields = ['fmea_id', 'title', 'description']
    readonly_fields = ['fmea_id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Identification', {
            'fields': ('fmea_id', 'title', 'fmea_type')
        }),
        ('Details', {
            'fields': ('product_line', 'description', 'status')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FMEARecord)
class FMEARecordAdmin(admin.ModelAdmin):
    list_display = ['worksheet', 'item_function', 'failure_mode', 'rpn_badge', 'completion_date']
    list_filter = ['worksheet', 'responsible_person', 'completion_date', 'created_at']
    search_fields = ['worksheet__fmea_id', 'failure_mode', 'failure_cause']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'rpn', 'new_rpn']

    fieldsets = (
        ('Worksheet', {
            'fields': ('worksheet', 'item_function')
        }),
        ('Failure Analysis', {
            'fields': ('failure_mode', 'failure_effect', 'failure_cause')
        }),
        ('Current Controls', {
            'fields': ('current_controls_prevention', 'current_controls_detection')
        }),
        ('Initial Scoring', {
            'fields': ('severity', 'occurrence', 'detection', 'rpn')
        }),
        ('Actions', {
            'fields': ('recommended_action', 'action_taken')
        }),
        ('New Scoring', {
            'fields': ('new_severity', 'new_occurrence', 'new_detection', 'new_rpn')
        }),
        ('Responsibility', {
            'fields': ('responsible_person', 'target_date', 'completion_date')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rpn_badge(self, obj):
        rpn = obj.rpn
        if rpn >= 300:
            color = '#d32f2f'
        elif rpn >= 150:
            color = '#f57c00'
        elif rpn >= 50:
            color = '#fbc02d'
        else:
            color = '#388e3c'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            rpn
        )
    rpn_badge.short_description = 'RPN'


@admin.register(RiskReport)
class RiskReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'title', 'report_type', 'status', 'overall_risk_acceptability']
    list_filter = ['status', 'report_type', 'overall_risk_acceptability', 'product_line', 'created_at']
    search_fields = ['report_id', 'title', 'description']
    readonly_fields = ['report_id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Identification', {
            'fields': ('report_id', 'title', 'report_type')
        }),
        ('Content', {
            'fields': ('product_line', 'description', 'benefit_risk_conclusion')
        }),
        ('Assessment', {
            'fields': ('overall_risk_acceptability', 'status')
        }),
        ('Linked Document', {
            'fields': ('linked_document',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RiskMonitoringAlert)
class RiskMonitoringAlertAdmin(admin.ModelAdmin):
    list_display = ['hazard', 'alert_type', 'acknowledgement_status', 'created_at']
    list_filter = ['alert_type', 'is_acknowledged', 'created_at']
    search_fields = ['hazard__hazard_id', 'message']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Alert Information', {
            'fields': ('hazard', 'alert_type', 'message')
        }),
        ('Values', {
            'fields': ('threshold_value', 'actual_value')
        }),
        ('Acknowledgement', {
            'fields': ('is_acknowledged', 'acknowledged_by', 'acknowledged_at')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def acknowledgement_status(self, obj):
        if obj.is_acknowledged:
            return format_html(
                '<span style="background-color: #388e3c; color: white; padding: 5px 10px; '
                'border-radius: 3px;">Acknowledged</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #f57c00; color: white; padding: 5px 10px; '
                'border-radius: 3px;">Pending</span>'
            )
    acknowledgement_status.short_description = 'Status'
