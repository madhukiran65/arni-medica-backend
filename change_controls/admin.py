from django.contrib import admin
from .models import (
    ChangeControl, ChangeControlApproval, ChangeControlTask,
    ChangeControlAttachment, ChangeControlComment
)


class ChangeControlApprovalInline(admin.TabularInline):
    model = ChangeControlApproval
    fields = ('approver', 'approval_role', 'status', 'sequence')
    extra = 0


class ChangeControlTaskInline(admin.TabularInline):
    model = ChangeControlTask
    fields = ('title', 'assigned_to', 'due_date', 'status')
    extra = 0


class ChangeControlAttachmentInline(admin.TabularInline):
    model = ChangeControlAttachment
    fields = ('file_name', 'uploaded_by', 'uploaded_at')
    extra = 0


@admin.register(ChangeControl)
class ChangeControlAdmin(admin.ModelAdmin):
    list_display = ('change_control_id', 'title', 'change_type', 'risk_level', 'current_stage', 'created_at')
    list_filter = ('change_type', 'risk_level', 'current_stage', 'is_emergency', 'created_at')
    search_fields = ('change_control_id', 'title', 'description')
    ordering = ['-created_at']
    inlines = [ChangeControlApprovalInline, ChangeControlTaskInline, ChangeControlAttachmentInline]


@admin.register(ChangeControlApproval)
class ChangeControlApprovalAdmin(admin.ModelAdmin):
    list_display = ('change_control', 'approver', 'status', 'approval_role', 'responded_at')
    list_filter = ('status', 'approval_role', 'responded_at')
    search_fields = ('change_control__change_control_id', 'approver__username')
    ordering = ['sequence']


@admin.register(ChangeControlTask)
class ChangeControlTaskAdmin(admin.ModelAdmin):
    list_display = ('change_control', 'title', 'assigned_to', 'due_date', 'status')
    list_filter = ('status', 'due_date', 'completed_date')
    search_fields = ('change_control__change_control_id', 'title', 'assigned_to__username')
    ordering = ['sequence']


@admin.register(ChangeControlAttachment)
class ChangeControlAttachmentAdmin(admin.ModelAdmin):
    list_display = ('change_control', 'file_name', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('change_control__change_control_id', 'file_name')
    ordering = ['-uploaded_at']


@admin.register(ChangeControlComment)
class ChangeControlCommentAdmin(admin.ModelAdmin):
    list_display = ('change_control', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('change_control__change_control_id', 'author__username', 'comment')
    ordering = ['-created_at']
