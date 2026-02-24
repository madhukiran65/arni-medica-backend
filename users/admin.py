from django.contrib import admin
from .models import Department, Role, UserProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'can_create_documents',
        'can_approve_documents',
        'can_sign_documents',
        'can_create_capa',
        'can_close_capa',
        'can_create_complaints',
        'can_log_training',
        'can_create_audit',
        'can_view_audit_trail',
        'can_manage_users'
    ]
    search_fields = ['name', 'description']
    filter_list = [
        'can_create_documents',
        'can_approve_documents',
        'can_sign_documents',
        'can_create_capa',
        'can_close_capa',
        'can_create_complaints',
        'can_log_training',
        'can_create_audit',
        'can_view_audit_trail',
        'can_manage_users'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Document Permissions', {
            'fields': ('can_create_documents', 'can_approve_documents', 'can_sign_documents')
        }),
        ('CAPA Permissions', {
            'fields': ('can_create_capa', 'can_close_capa')
        }),
        ('Complaints Permissions', {
            'fields': ('can_create_complaints',)
        }),
        ('Training Permissions', {
            'fields': ('can_log_training',)
        }),
        ('Audit Permissions', {
            'fields': ('can_create_audit', 'can_view_audit_trail')
        }),
        ('User Management', {
            'fields': ('can_manage_users',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'employee_id', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'roles', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']
    filter_horizontal = ['roles']
    readonly_fields = ['created_at', 'updated_at', 'user']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Department and Roles', {
            'fields': ('department', 'roles')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
