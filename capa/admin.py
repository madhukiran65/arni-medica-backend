from django.contrib import admin
from .models import CAPA, CAPAApproval, CAPADocument, CAPAComment


class CAPAApprovalInline(admin.TabularInline):
    model = CAPAApproval
    fields = ('phase', 'approver', 'status', 'sequence')
    extra = 0


class CAPADocumentInline(admin.TabularInline):
    model = CAPADocument
    fields = ('phase', 'document_type', 'title')
    extra = 0


@admin.register(CAPA)
class CAPAAdmin(admin.ModelAdmin):
    list_display = ('capa_id', 'title', 'source', 'priority', 'current_phase', 'created_at')
    list_filter = ('source', 'priority', 'current_phase', 'capa_type', 'created_at')
    search_fields = ('capa_id', 'title', 'description')
    ordering = ['-created_at']
    inlines = [CAPAApprovalInline, CAPADocumentInline]


@admin.register(CAPAApproval)
class CAPAApprovalAdmin(admin.ModelAdmin):
    list_display = ('capa', 'phase', 'approver', 'status', 'responded_at')
    list_filter = ('phase', 'status', 'approval_tier')
    search_fields = ('capa__capa_id', 'approver__username')
    ordering = ['sequence']


@admin.register(CAPADocument)
class CAPADocumentAdmin(admin.ModelAdmin):
    list_display = ('capa', 'phase', 'document_type', 'title', 'uploaded_at')
    list_filter = ('phase', 'document_type', 'uploaded_at')
    search_fields = ('capa__capa_id', 'title')
    ordering = ['-uploaded_at']


@admin.register(CAPAComment)
class CAPACommentAdmin(admin.ModelAdmin):
    list_display = ('capa', 'author', 'phase', 'created_at')
    list_filter = ('phase', 'created_at')
    search_fields = ('capa__capa_id', 'author__username', 'comment')
    ordering = ['-created_at']
