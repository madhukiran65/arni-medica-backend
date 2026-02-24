from django.contrib import admin
from documents.models import (
    Document,
    DocumentVersion,
    DocumentChangeOrder,
    DocumentChangeApproval,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'document_id',
        'title',
        'document_type',
        'status',
        'department',
        'owner',
        'created_at',
    ]
    list_filter = [
        'status',
        'document_type',
        'department',
        'requires_approval',
        'created_at',
    ]
    search_fields = ['document_id', 'title', 'description']
    readonly_fields = ['file_hash', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Document Information', {
            'fields': ('document_id', 'title', 'document_type', 'department', 'owner')
        }),
        ('Content', {
            'fields': ('description', 'file', 'file_hash')
        }),
        ('Versioning', {
            'fields': ('version', 'revision_number')
        }),
        ('Status & Dates', {
            'fields': (
                'status',
                'effective_date',
                'next_review_date',
                'requires_approval',
            )
        }),
        ('AI Classification', {
            'fields': ('ai_classification', 'ai_confidence')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = [
        'document',
        'version_number',
        'created_by',
        'created_at',
    ]
    list_filter = ['document', 'created_at']
    search_fields = ['document__document_id', 'document__title', 'version_number']
    readonly_fields = ['file_hash', 'created_at']
    fieldsets = (
        ('Version Information', {
            'fields': ('document', 'version_number', 'created_by', 'created_at')
        }),
        ('Content', {
            'fields': ('file', 'file_hash', 'change_summary')
        }),
    )
    ordering = ['-created_at']


@admin.register(DocumentChangeOrder)
class DocumentChangeOrderAdmin(admin.ModelAdmin):
    list_display = [
        'dco_number',
        'title',
        'status',
        'change_type',
        'estimated_review_days',
        'created_at',
    ]
    list_filter = [
        'status',
        'change_type',
        'created_at',
    ]
    search_fields = ['dco_number', 'title', 'reason']
    filter_horizontal = ['affected_documents']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Change Order Information', {
            'fields': ('dco_number', 'title', 'change_type')
        }),
        ('Details', {
            'fields': ('reason', 'affected_documents', 'estimated_review_days')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']


@admin.register(DocumentChangeApproval)
class DocumentChangeApprovalAdmin(admin.ModelAdmin):
    list_display = [
        'dco',
        'approver',
        'status',
        'approved_at',
        'created_at',
    ]
    list_filter = [
        'status',
        'dco__status',
        'approved_at',
        'created_at',
    ]
    search_fields = ['dco__dco_number', 'approver__username', 'comments']
    readonly_fields = ['signature_hash', 'created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Approval Information', {
            'fields': ('dco', 'approver', 'status')
        }),
        ('Approval Details', {
            'fields': ('comments', 'signature_hash', 'approved_at')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-created_at']
