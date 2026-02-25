from django.contrib import admin
from .models import AuditLog, Attachment, ElectronicSignature


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
        'signer', 'reason', 'signed_at', 'content_type',
        'object_id', 'ip_address',
    ]
    list_filter = ['reason', 'signed_at', 'content_type']
    search_fields = ['signer__username', 'meaning']
    readonly_fields = [
        'content_type', 'object_id', 'signer', 'signed_at',
        'reason', 'meaning', 'content_hash', 'signature_hash', 'ip_address',
    ]
    date_hierarchy = 'signed_at'
    ordering = ['-signed_at']

    def has_add_permission(self, request):
        return False  # Signatures are system-generated

    def has_change_permission(self, request, obj=None):
        return False  # Immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Immutable
