from django.contrib import admin
from django.utils.html import format_html

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


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    """Admin for Complaint"""

    list_display = [
        'complaint_id',
        'title',
        'product_name',
        'status_badge',
        'severity_badge',
        'is_reportable_to_fda',
        'received_date',
        'assigned_to',
    ]
    list_filter = [
        'status',
        'severity',
        'event_type',
        'is_reportable_to_fda',
        'mdr_submission_status',
        'received_date',
    ]
    search_fields = ['complaint_id', 'title', 'product_name', 'complainant_name']
    readonly_fields = ['complaint_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('complaint_id', 'title', 'description'),
        }),
        ('Complainant', {
            'fields': ('complainant_name', 'complainant_email', 'complainant_phone', 'complainant_organization', 'complainant_type'),
        }),
        ('Product Information', {
            'fields': ('product_name', 'product_code', 'product_lot_number', 'product_serial_number', 'manufacture_date', 'expiry_date'),
        }),
        ('Event Details', {
            'fields': ('event_date', 'event_description', 'event_location', 'event_country'),
        }),
        ('Classification', {
            'fields': ('category', 'severity', 'priority'),
        }),
        ('FDA 3500A', {
            'fields': ('event_type', 'patient_age', 'patient_sex', 'health_effect'),
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to', 'department', 'coordinator'),
        }),
        ('Investigation', {
            'fields': ('investigation_summary', 'root_cause', 'investigated_by'),
        }),
        ('MDR Submission', {
            'fields': ('is_reportable_to_fda', 'mdr_submission_status', 'mdr_report_number', 'mdr_submission_date'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'new': '#FFC107',
            'under_investigation': '#17A2B8',
            'investigation_complete': '#28A745',
            'capa_initiated': '#FFC107',
            'closed': '#6C757D',
            'rejected': '#DC3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'

    def severity_badge(self, obj):
        colors = {
            'critical': '#DC3545',
            'major': '#FFC107',
            'minor': '#17A2B8',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.severity, '#000000'),
            obj.get_severity_display(),
        )
    severity_badge.short_description = 'Severity'


@admin.register(ComplaintAttachment)
class ComplaintAttachmentAdmin(admin.ModelAdmin):
    """Admin for ComplaintAttachment"""

    list_display = ['file_name', 'complaint', 'attachment_type', 'uploaded_at', 'uploaded_by']
    list_filter = ['attachment_type', 'uploaded_at']
    search_fields = ['file_name', 'complaint__complaint_id']
    readonly_fields = ['uploaded_at']


@admin.register(MIRRecord)
class MIRRecordAdmin(admin.ModelAdmin):
    """Admin for MIRRecord"""

    list_display = ['mir_number', 'complaint', 'report_type', 'submitted_date']
    list_filter = ['report_type', 'submitted_date']
    search_fields = ['mir_number', 'complaint__complaint_id']
    readonly_fields = ['mir_number', 'created_at', 'updated_at', 'created_by', 'updated_by']


@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    """Admin for ComplaintComment"""

    list_display = ['complaint', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['complaint__complaint_id', 'author__username', 'comment']
    readonly_fields = ['created_at']


# ============================================================================
# PMS (Post-Market Surveillance) Admin - Migrated from pms app
# ============================================================================


@admin.register(PMSPlan)
class PMSPlanAdmin(admin.ModelAdmin):
    """Admin for PMSPlan"""

    list_display = [
        'plan_id',
        'title',
        'product_name',
        'status_badge',
        'review_frequency',
        'responsible_person',
        'effective_date',
        'created_at',
    ]
    list_filter = [
        'status',
        'review_frequency',
        'product_line',
        'department',
        'created_at',
    ]
    search_fields = ['plan_id', 'title', 'product_name']
    readonly_fields = ['plan_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('plan_id', 'title', 'product_name'),
        }),
        ('Organization', {
            'fields': ('product_line', 'department', 'responsible_person'),
        }),
        ('Plan Details', {
            'fields': ('plan_version', 'data_sources', 'monitoring_criteria', 'review_frequency'),
        }),
        ('Dates', {
            'fields': ('effective_date', 'next_review_date'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'draft': '#FFC107',
            'active': '#28A745',
            'under_review': '#17A2B8',
            'closed': '#6C757D',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(TrendAnalysis)
class TrendAnalysisAdmin(admin.ModelAdmin):
    """Admin for TrendAnalysis"""

    list_display = [
        'trend_id',
        'pms_plan',
        'analysis_period_start',
        'trend_direction',
        'threshold_breached_badge',
        'status_badge',
        'analyzed_by',
        'created_at',
    ]
    list_filter = [
        'status',
        'trend_direction',
        'threshold_breached',
        'statistical_method',
        'product_line',
        'created_at',
    ]
    search_fields = ['trend_id', 'pms_plan__title', 'analysis_summary']
    readonly_fields = ['trend_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('trend_id', 'pms_plan', 'product_line'),
        }),
        ('Analysis Period', {
            'fields': ('analysis_period_start', 'analysis_period_end'),
        }),
        ('Data', {
            'fields': ('complaint_count', 'complaint_rate', 'previous_period_rate'),
        }),
        ('Analysis', {
            'fields': ('trend_direction', 'threshold_breached', 'statistical_method', 'analysis_summary'),
        }),
        ('Findings & Actions', {
            'fields': ('key_findings', 'recommended_actions'),
        }),
        ('Review', {
            'fields': ('analyzed_by', 'status'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def threshold_breached_badge(self, obj):
        if obj.threshold_breached:
            return format_html(
                '<span style="color: #DC3545; font-weight: bold;">YES</span>'
            )
        return format_html('<span style="color: #28A745;">NO</span>')
    threshold_breached_badge.short_description = 'Threshold Breached'

    def status_badge(self, obj):
        colors = {
            'draft': '#FFC107',
            'reviewed': '#17A2B8',
            'approved': '#28A745',
            'action_required': '#DC3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(PMSReport)
class PMSReportAdmin(admin.ModelAdmin):
    """Admin for PMSReport"""

    list_display = [
        'report_id',
        'title',
        'report_type',
        'period_start',
        'period_end',
        'status_badge',
        'submitted_to',
        'created_at',
    ]
    list_filter = [
        'status',
        'report_type',
        'submitted_to',
        'product_line',
        'created_at',
    ]
    search_fields = ['report_id', 'title', 'pms_plan__title']
    readonly_fields = ['report_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('report_id', 'title', 'report_type'),
        }),
        ('Scope', {
            'fields': ('pms_plan', 'product_line', 'period_start', 'period_end'),
        }),
        ('Content', {
            'fields': ('executive_summary', 'conclusions', 'recommendations'),
        }),
        ('Documentation', {
            'fields': ('linked_document',),
        }),
        ('Status', {
            'fields': ('status', 'submitted_to', 'submission_date', 'approved_by'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'draft': '#FFC107',
            'in_review': '#17A2B8',
            'approved': '#28A745',
            'submitted': '#6C757D',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(VigilanceReport)
class VigilanceReportAdmin(admin.ModelAdmin):
    """Admin for VigilanceReport"""

    list_display = [
        'vigilance_id',
        'complaint',
        'authority',
        'report_type',
        'patient_outcome_badge',
        'status_badge',
        'submission_deadline',
        'created_at',
    ]
    list_filter = [
        'status',
        'authority',
        'report_type',
        'report_form',
        'patient_outcome',
        'created_at',
    ]
    search_fields = ['vigilance_id', 'complaint__complaint_id', 'tracking_number']
    readonly_fields = ['vigilance_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('vigilance_id', 'complaint'),
        }),
        ('Regulatory', {
            'fields': ('authority', 'report_form', 'report_type'),
        }),
        ('Submission', {
            'fields': ('submission_deadline', 'actual_submission_date', 'tracking_number', 'submitted_by'),
        }),
        ('Device Information', {
            'fields': ('device_udi', 'lot_number'),
        }),
        ('Clinical Details', {
            'fields': ('narrative', 'patient_outcome'),
        }),
        ('Authority Response', {
            'fields': ('authority_response', 'response_date'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def patient_outcome_badge(self, obj):
        if obj.patient_outcome:
            severity_colors = {
                'death': '#DC3545',
                'life_threatening': '#DC3545',
                'hospitalization': '#FFC107',
                'disability': '#FFC107',
                'congenital_anomaly': '#DC3545',
                'intervention_required': '#FFC107',
                'other': '#17A2B8',
                'unknown': '#6C757D',
            }
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
                severity_colors.get(obj.patient_outcome, '#000000'),
                obj.get_patient_outcome_display(),
            )
        return '-'
    patient_outcome_badge.short_description = 'Patient Outcome'

    def status_badge(self, obj):
        colors = {
            'draft': '#FFC107',
            'pending_submission': '#17A2B8',
            'submitted': '#28A745',
            'acknowledged': '#6C757D',
            'closed': '#6C757D',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(LiteratureReview)
class LiteratureReviewAdmin(admin.ModelAdmin):
    """Admin for LiteratureReview"""

    list_display = [
        'review_id',
        'title',
        'search_date',
        'articles_found',
        'articles_relevant',
        'safety_signals_badge',
        'status_badge',
        'reviewed_by',
        'created_at',
    ]
    list_filter = [
        'status',
        'safety_signals_identified',
        'pms_plan',
        'created_at',
    ]
    search_fields = ['review_id', 'title', 'pms_plan__title']
    readonly_fields = ['review_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('review_id', 'title', 'pms_plan'),
        }),
        ('Search Details', {
            'fields': ('search_strategy', 'databases_searched', 'search_date'),
        }),
        ('Results', {
            'fields': ('articles_found', 'articles_relevant'),
        }),
        ('Findings', {
            'fields': ('key_findings', 'safety_signals_identified', 'signal_description'),
        }),
        ('Review', {
            'fields': ('reviewed_by', 'status'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def safety_signals_badge(self, obj):
        if obj.safety_signals_identified:
            return format_html(
                '<span style="color: #DC3545; font-weight: bold;">YES</span>'
            )
        return format_html('<span style="color: #28A745;">NO</span>')
    safety_signals_badge.short_description = 'Safety Signals'

    def status_badge(self, obj):
        colors = {
            'planned': '#FFC107',
            'in_progress': '#17A2B8',
            'completed': '#28A745',
            'action_required': '#DC3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(SafetySignal)
class SafetySignalAdmin(admin.ModelAdmin):
    """Admin for SafetySignal"""

    list_display = [
        'signal_id',
        'title',
        'source',
        'detection_date',
        'severity_badge',
        'status_badge',
        'linked_pms_plan',
        'created_at',
    ]
    list_filter = [
        'status',
        'severity',
        'source',
        'product_line',
        'created_at',
    ]
    search_fields = ['signal_id', 'title', 'description']
    readonly_fields = ['signal_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Identification', {
            'fields': ('signal_id', 'title', 'source'),
        }),
        ('Details', {
            'fields': ('description', 'detection_date', 'product_line'),
        }),
        ('Assessment', {
            'fields': ('severity', 'evaluation_summary', 'risk_assessment', 'action_taken'),
        }),
        ('Linking', {
            'fields': ('linked_capa', 'linked_pms_plan'),
        }),
        ('Review', {
            'fields': ('evaluated_by', 'status'),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )

    def severity_badge(self, obj):
        colors = {
            'critical': '#DC3545',
            'major': '#FFC107',
            'minor': '#17A2B8',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.severity, '#000000'),
            obj.get_severity_display(),
        )
    severity_badge.short_description = 'Severity'

    def status_badge(self, obj):
        colors = {
            'detected': '#FFC107',
            'under_evaluation': '#17A2B8',
            'confirmed': '#DC3545',
            'refuted': '#28A745',
            'closed': '#6C757D',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'
