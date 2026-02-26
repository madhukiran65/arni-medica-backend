from django.contrib import admin
from .models import (
    DesignProject,
    UserNeed,
    DesignInput,
    DesignOutput,
    VVProtocol,
    DesignReview,
    DesignTransfer,
    TraceabilityLink,
)


@admin.register(DesignProject)
class DesignProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'title', 'product_type', 'current_phase', 'status', 'project_lead', 'created_at']
    list_filter = ['status', 'current_phase', 'product_type', 'regulatory_pathway', 'created_at']
    search_fields = ['project_id', 'title', 'description']
    readonly_fields = ['project_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('project_id', 'title', 'description')
        }),
        ('Product Details', {
            'fields': ('product_type', 'product_line', 'department')
        }),
        ('Regulatory & Status', {
            'fields': ('regulatory_pathway', 'current_phase', 'status')
        }),
        ('Management', {
            'fields': ('project_lead', 'target_completion_date')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserNeed)
class UserNeedAdmin(admin.ModelAdmin):
    list_display = ['need_id', 'project', 'source', 'priority', 'status', 'created_at']
    list_filter = ['source', 'priority', 'status', 'created_at']
    search_fields = ['need_id', 'description', 'project__title']
    readonly_fields = ['need_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('need_id', 'project', 'description')
        }),
        ('Details', {
            'fields': ('source', 'priority', 'acceptance_criteria', 'rationale')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DesignInput)
class DesignInputAdmin(admin.ModelAdmin):
    list_display = ['input_id', 'project', 'input_type', 'status', 'created_at']
    list_filter = ['input_type', 'status', 'created_at']
    search_fields = ['input_id', 'specification', 'project__title']
    readonly_fields = ['input_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    filter_horizontal = ['linked_user_needs']
    fieldsets = (
        ('Basic Information', {
            'fields': ('input_id', 'project', 'specification')
        }),
        ('Criteria & Testing', {
            'fields': ('input_type', 'measurable_criteria', 'tolerance', 'test_method')
        }),
        ('Links', {
            'fields': ('linked_user_needs',)
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DesignOutput)
class DesignOutputAdmin(admin.ModelAdmin):
    list_display = ['output_id', 'project', 'output_type', 'revision', 'status', 'created_at']
    list_filter = ['output_type', 'status', 'created_at']
    search_fields = ['output_id', 'description', 'project__title']
    readonly_fields = ['output_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    filter_horizontal = ['linked_inputs']
    fieldsets = (
        ('Basic Information', {
            'fields': ('output_id', 'project', 'description')
        }),
        ('Details', {
            'fields': ('output_type', 'revision', 'file')
        }),
        ('Links', {
            'fields': ('linked_inputs',)
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VVProtocol)
class VVProtocolAdmin(admin.ModelAdmin):
    list_display = ['protocol_id', 'project', 'protocol_type', 'status', 'result', 'execution_date', 'created_at']
    list_filter = ['protocol_type', 'status', 'result', 'created_at']
    search_fields = ['protocol_id', 'title', 'project__title']
    readonly_fields = ['protocol_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    filter_horizontal = ['linked_inputs', 'linked_outputs']
    fieldsets = (
        ('Basic Information', {
            'fields': ('protocol_id', 'project', 'title', 'protocol_type')
        }),
        ('Protocol Details', {
            'fields': ('test_method', 'acceptance_criteria', 'sample_size')
        }),
        ('Links', {
            'fields': ('linked_inputs', 'linked_outputs')
        }),
        ('Execution', {
            'fields': ('execution_date', 'result', 'result_summary', 'deviations_noted', 'executed_by')
        }),
        ('Files', {
            'fields': ('file', 'result_file')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DesignReview)
class DesignReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'project', 'phase', 'review_date', 'status', 'outcome', 'created_at']
    list_filter = ['phase', 'status', 'outcome', 'review_date', 'created_at']
    search_fields = ['review_id', 'project__title']
    readonly_fields = ['review_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    filter_horizontal = ['attendees']
    fieldsets = (
        ('Basic Information', {
            'fields': ('review_id', 'project', 'phase', 'review_date')
        }),
        ('Attendees & Content', {
            'fields': ('attendees', 'agenda', 'minutes')
        }),
        ('Outcome', {
            'fields': ('outcome', 'conditions', 'action_items', 'follow_up_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DesignTransfer)
class DesignTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_id', 'project', 'status', 'manufacturing_site', 'production_readiness_confirmed', 'created_at']
    list_filter = ['status', 'production_readiness_confirmed', 'created_at']
    search_fields = ['transfer_id', 'project__title']
    readonly_fields = ['transfer_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('transfer_id', 'project', 'description')
        }),
        ('Manufacturing', {
            'fields': ('manufacturing_site', 'transfer_checklist')
        }),
        ('Readiness', {
            'fields': ('production_readiness_confirmed', 'confirmed_by', 'confirmed_date')
        }),
        ('Documentation', {
            'fields': ('linked_document',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TraceabilityLink)
class TraceabilityLinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'link_status', 'user_need', 'design_input', 'design_output', 'vv_protocol', 'created_at']
    list_filter = ['link_status', 'project', 'created_at']
    search_fields = ['project__title', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Link Information', {
            'fields': ('project', 'link_status', 'gap_description', 'notes')
        }),
        ('Traced Items', {
            'fields': ('user_need', 'design_input', 'design_output', 'vv_protocol')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
