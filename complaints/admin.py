from django.contrib import admin
from .models import Complaint, ComplaintAttachment, MIRRecord, ComplaintComment


class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    fields = ('file_name', 'attachment_type', 'uploaded_by', 'uploaded_at')
    extra = 0


class MIRRecordInline(admin.TabularInline):
    model = MIRRecord
    fields = ('mir_number', 'report_type', 'submitted_to')
    extra = 0


class ComplaintCommentInline(admin.TabularInline):
    model = ComplaintComment
    fields = ('author', 'comment', 'created_at')
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'title', 'status', 'severity', 'priority', 'created_at')
    list_filter = ('status', 'severity', 'priority', 'category', 'is_reportable_to_fda', 'created_at')
    search_fields = ('complaint_id', 'title', 'product_name', 'complainant_name')
    ordering = ['-created_at']
    inlines = [ComplaintAttachmentInline, MIRRecordInline, ComplaintCommentInline]


@admin.register(ComplaintAttachment)
class ComplaintAttachmentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'file_name', 'attachment_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('attachment_type', 'uploaded_at')
    search_fields = ('complaint__complaint_id', 'file_name')
    ordering = ['-uploaded_at']


@admin.register(MIRRecord)
class MIRRecordAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'mir_number', 'report_type', 'submitted_to', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('complaint__complaint_id', 'mir_number')
    ordering = ['-created_at']


@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('complaint__complaint_id', 'author__username', 'comment')
    ordering = ['-created_at']
