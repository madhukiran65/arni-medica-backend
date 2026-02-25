from django.contrib import admin
from .models import Deviation, DeviationAttachment, DeviationComment


class DeviationAttachmentInline(admin.TabularInline):
    model = DeviationAttachment
    fields = ('file_name', 'file_type', 'uploaded_by', 'uploaded_at')
    extra = 0


class DeviationCommentInline(admin.TabularInline):
    model = DeviationComment
    fields = ('author', 'comment', 'stage', 'created_at')
    extra = 0


@admin.register(Deviation)
class DeviationAdmin(admin.ModelAdmin):
    list_display = ('deviation_id', 'title', 'deviation_type', 'severity', 'current_stage', 'created_at')
    list_filter = ('deviation_type', 'severity', 'category', 'current_stage', 'created_at')
    search_fields = ('deviation_id', 'title', 'description')
    ordering = ['-created_at']
    inlines = [DeviationAttachmentInline, DeviationCommentInline]


@admin.register(DeviationAttachment)
class DeviationAttachmentAdmin(admin.ModelAdmin):
    list_display = ('deviation', 'file_name', 'file_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('deviation__deviation_id', 'file_name')
    ordering = ['-uploaded_at']


@admin.register(DeviationComment)
class DeviationCommentAdmin(admin.ModelAdmin):
    list_display = ('deviation', 'author', 'stage', 'created_at')
    list_filter = ('stage', 'created_at')
    search_fields = ('deviation__deviation_id', 'author__username', 'comment')
    ordering = ['-created_at']
