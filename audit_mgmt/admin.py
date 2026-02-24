from django.contrib import admin
from .models import AuditPlan, AuditFinding


@admin.register(AuditPlan)
class AuditPlanAdmin(admin.ModelAdmin):
    list_display = ['audit_id', 'audit_type', 'status', 'lead_auditor', 'planned_start_date', 'major_nc', 'minor_nc']
    list_filter = ['audit_type', 'status', 'planned_start_date', 'created_at']
    search_fields = ['audit_id', 'scope', 'supplier']
    readonly_fields = ['findings_count', 'major_nc', 'minor_nc', 'observations', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('audit_id', 'audit_type', 'scope', 'supplier')
        }),
        ('Status & Dates', {
            'fields': ('status', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Team', {
            'fields': ('lead_auditor',)
        }),
        ('Findings Summary', {
            'fields': ('findings_count', 'major_nc', 'minor_nc', 'observations')
        }),
        ('Future Planning', {
            'fields': ('next_audit_planned',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ['finding_id', 'audit', 'category', 'status', 'target_closure_date', 'assigned_capa']
    list_filter = ['category', 'status', 'created_at', 'target_closure_date']
    search_fields = ['finding_id', 'description', 'evidence']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('audit', 'finding_id', 'category')
        }),
        ('Details', {
            'fields': ('description', 'evidence')
        }),
        ('Status & CAPA', {
            'fields': ('status', 'assigned_capa')
        }),
        ('Closure Tracking', {
            'fields': ('target_closure_date', 'actual_closure_date')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
