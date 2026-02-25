from django.contrib import admin
from .models import (
    DocumentInfocardType, DocumentSubType, DocumentCheckout,
    DocumentApprover, DocumentSnapshot, DocumentVersion,
    DocumentChangeOrder, DocumentChangeApproval, Document
)


@admin.register(DocumentInfocardType)
class DocumentInfocardTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'prefix', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'prefix')
    ordering = ['-created_at']


@admin.register(DocumentSubType)
class DocumentSubTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'infocard_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'infocard_type', 'created_at')
    search_fields = ('name',)
    ordering = ['-created_at']


@admin.register(DocumentCheckout)
class DocumentCheckoutAdmin(admin.ModelAdmin):
    list_display = ('document', 'checked_out_by', 'checked_out_at', 'expected_checkin_date')
    list_filter = ('checked_out_at', 'is_active')
    search_fields = ('document__title', 'checked_out_by__username')
    ordering = ['-checked_out_at']


@admin.register(DocumentApprover)
class DocumentApproverAdmin(admin.ModelAdmin):
    list_display = ('document', 'approver', 'sequence', 'approval_status')
    list_filter = ('approval_status', 'sequence')
    search_fields = ('document__title', 'approver__username')
    ordering = ['sequence']


@admin.register(DocumentSnapshot)
class DocumentSnapshotAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_string', 'snapshot_type', 'created_at')
    list_filter = ('snapshot_type', 'created_at')
    search_fields = ('document__title', 'version_string')
    ordering = ['-created_at']


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'major_version', 'minor_version', 'change_type', 'released_date')
    list_filter = ('change_type', 'is_major_change', 'released_date')
    search_fields = ('document__title', 'change_summary')
    ordering = ['-released_date']


@admin.register(DocumentChangeOrder)
class DocumentChangeOrderAdmin(admin.ModelAdmin):
    list_display = ('change_number', 'document', 'title', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'regulatory_impact')
    search_fields = ('change_number', 'title', 'document__title')
    ordering = ['-created_at']


@admin.register(DocumentChangeApproval)
class DocumentChangeApprovalAdmin(admin.ModelAdmin):
    list_display = ('change_order', 'approver', 'status', 'approved_at')
    list_filter = ('status', 'approved_at')
    search_fields = ('change_order__change_number', 'approver__username')
    ordering = ['-approved_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'title', 'vault_state', 'created_at')
    list_filter = ('vault_state', 'created_at')
    search_fields = ('document_id', 'title', 'description')
    ordering = ['-created_at']
