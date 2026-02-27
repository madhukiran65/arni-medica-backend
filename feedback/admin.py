from django.contrib import admin
from .models import FeedbackTicket, FeedbackAttachment


class FeedbackAttachmentInline(admin.TabularInline):
    model = FeedbackAttachment
    extra = 0
    readonly_fields = ['file_name', 'file_type', 'file_size', 'uploaded_by', 'uploaded_at']


@admin.register(FeedbackTicket)
class FeedbackTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'type', 'title', 'priority', 'status', 'submitted_by', 'created_at']
    list_filter = ['type', 'priority', 'status', 'module', 'created_at']
    search_fields = ['ticket_id', 'title', 'description']
    readonly_fields = ['ticket_id', 'created_by', 'created_at', 'updated_by', 'updated_at']
    inlines = [FeedbackAttachmentInline]
