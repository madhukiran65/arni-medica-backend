from django.contrib import admin
from .models import Complaint, ComplaintInvestigation


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['complaint_id', 'product', 'severity', 'status', 'assigned_to', 'complaint_date', 'created_at']
    list_filter = ['severity', 'status', 'reportable', 'complaint_date', 'created_at']
    search_fields = ['complaint_id', 'product', 'customer', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('complaint_id', 'product', 'batch_lot', 'customer')
        }),
        ('Details', {
            'fields': ('description', 'complaint_date', 'severity', 'reportable')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to')
        }),
        ('Investigation', {
            'fields': ('investigation_summary', 'root_cause', 'impact_assessment')
        }),
        ('CAPA Link', {
            'fields': ('related_capa',)
        }),
        ('AI Insights', {
            'fields': ('ai_triage', 'ai_confidence')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComplaintInvestigation)
class ComplaintInvestigationAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'investigator', 'investigation_step', 'investigation_date', 'created_at']
    list_filter = ['investigation_date', 'created_at']
    search_fields = ['complaint__complaint_id', 'investigation_step', 'findings']
    readonly_fields = ['investigation_date', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('complaint', 'investigator', 'investigation_step')
        }),
        ('Findings', {
            'fields': ('findings',)
        }),
        ('Audit Trail', {
            'fields': ('investigation_date', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
