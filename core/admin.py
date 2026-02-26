from django.contrib import admin
from .models import AuditLog, Attachment, ElectronicSignature, Notification


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only admin for immutable audit trail (21 CFR Part 11)"""
    list_display = [
        'timestamp', 'user', 'action', 'content_type',
        'object_id', 'object_repr', 'ip_address',
    ]
    list_filter = ['action', 'content_type', 'timestamp']
    search_fields = ['object_repr', 'change_summary', 'user__username']
    readonly_fields = [
        'content_type', 'object_id', 'object_repr', 'user', 'action',
        'timestamp', 'ip_address', 'old_values', 'new_values', 'change_summary',
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False  # Audit logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False  # Immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Immutable


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['file_name', 'description']
    readonly_fields = ['file_hash', 'uploaded_at']


@admin.register(ElectronicSignature)
class ElectronicSignatureAdmin(admin.ModelAdmin):
    """Read-only admin for electronic signatures (21 CFR Part 11)"""
    list_display = [
        'signer', 'signature_meaning', 'timestamp', 'is_valid',
        'content_type', 'object_id', 'ip_address',
    ]
    list_filter = ['signature_meaning', 'timestamp', 'is_valid', 'content_type']
    search_fields = ['signer__username', 'meaning', 'invalidation_reason']
    readonly_fields = [
        'content_type', 'object_id', 'signer', 'timestamp',
        'signature_meaning', 'reason', 'meaning', 'content_hash', 'signature_hash',
        'ip_address', 'is_valid', 'invalidated_by', 'invalidated_at', 'invalidation_reason',
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False  # Signatures are system-generated

    def has_change_permission(self, request, obj=None):
        return False  # Immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Immutable


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for user notifications"""
    list_display = [
        'subject', 'recipient', 'notification_type',
        'is_read', 'sent_at', 'read_at',
    ]
    list_filter = ['notification_type', 'is_read', 'sent_at']
    search_fields = ['subject', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = [
        'recipient', 'notification_type', 'subject', 'message',
        'related_object_type', 'related_object_id', 'sent_at', 'read_at',
    ]
    date_hierarchy = 'sent_at'
    ordering = ['-sent_at']

    def has_add_permission(self, request):
        return False  # Notifications are system-generated only
