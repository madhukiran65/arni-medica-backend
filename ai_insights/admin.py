from django.contrib import admin
from .models import AIInsight


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'insight_type', 'severity', 'confidence', 'is_acted_upon', 'created_at']
    list_filter = ['insight_type', 'severity', 'is_acted_upon', 'created_at']
    search_fields = ['title', 'description', 'model_used']
    readonly_fields = ['created_at', 'content_object']
    fieldsets = (
        ('Basic Information', {
            'fields': ('insight_type', 'title', 'description')
        }),
        ('Analysis', {
            'fields': ('confidence', 'severity', 'model_used')
        }),
        ('Related Content', {
            'fields': ('content_type', 'object_id', 'content_object')
        }),
        ('Action', {
            'fields': ('is_acted_upon', 'action_taken')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
