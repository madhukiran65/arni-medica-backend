from django.contrib import admin
from .models import TrainingCourse, TrainingAssignment


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ['course_id', 'title', 'course_type', 'duration_hours', 'is_mandatory', 'renewal_frequency_months']
    list_filter = ['course_type', 'is_mandatory', 'renewal_frequency_months']
    search_fields = ['course_id', 'title', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_id', 'title', 'description', 'course_type')
        }),
        ('Details', {
            'fields': ('duration_hours', 'renewal_frequency_months', 'is_mandatory')
        }),
        ('Regulatory', {
            'fields': ('regulatory_requirement',)
        }),
    )


@admin.register(TrainingAssignment)
class TrainingAssignmentAdmin(admin.ModelAdmin):
    list_display = ['assigned_to', 'course', 'status', 'due_date', 'completion_date', 'passed', 'score']
    list_filter = ['status', 'course', 'due_date', 'passed', 'created_at']
    search_fields = ['assigned_to__first_name', 'assigned_to__last_name', 'course__title']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Assignment Information', {
            'fields': ('course', 'assigned_to', 'assigned_by')
        }),
        ('Dates', {
            'fields': ('due_date', 'completion_date')
        }),
        ('Status & Results', {
            'fields': ('status', 'score', 'passed')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
