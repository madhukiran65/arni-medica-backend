from django.contrib import admin
from .models import CAPA, CAPAAction


@admin.register(CAPA)
class CAPAAdmin(admin.ModelAdmin):
    list_display = ['capa_id', 'title', 'status', 'priority', 'owner', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'source', 'created_at']
    search_fields = ['capa_id', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('capa_id', 'title', 'source', 'priority', 'owner')
        }),
        ('Status & Dates', {
            'fields': ('status', 'due_date', 'completed_date')
        }),
        ('Details', {
            'fields': ('description', 'root_cause', 'root_cause_analysis_method')
        }),
        ('Actions', {
            'fields': ('corrective_actions', 'preventive_actions')
        }),
        ('Verification', {
            'fields': ('verification_method', 'verification_results', 'verification_date')
        }),
        ('AI Insights', {
            'fields': ('ai_root_cause', 'ai_confidence')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CAPAAction)
class CAPAActionAdmin(admin.ModelAdmin):
    list_display = ['capa', 'action_type', 'responsible', 'status', 'target_date', 'completion_date']
    list_filter = ['action_type', 'status', 'target_date', 'created_at']
    search_fields = ['capa__capa_id', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('capa', 'action_type', 'description', 'responsible')
        }),
        ('Dates', {
            'fields': ('target_date', 'completion_date', 'status')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
