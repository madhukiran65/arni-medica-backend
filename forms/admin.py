from django.contrib import admin
from .models import (
    FormTemplate, FormSection, FormQuestion, FormInstance, FormResponse
)


class FormSectionInline(admin.TabularInline):
    model = FormSection
    fields = ('title', 'sequence', 'is_repeatable')
    extra = 0


class FormQuestionInline(admin.TabularInline):
    model = FormQuestion
    fields = ('question_text', 'question_type', 'is_required', 'sequence')
    extra = 0


class FormResponseInline(admin.TabularInline):
    model = FormResponse
    fields = ('question', 'response_text', 'answered_at')
    extra = 0


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'version', 'is_published', 'is_active')
    list_filter = ('template_type', 'is_published', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ['-created_at']
    inlines = [FormSectionInline]


@admin.register(FormSection)
class FormSectionAdmin(admin.ModelAdmin):
    list_display = ('template', 'title', 'sequence', 'is_repeatable')
    list_filter = ('is_repeatable', 'sequence')
    search_fields = ('template__name', 'title')
    ordering = ['sequence']
    inlines = [FormQuestionInline]


@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('section', 'question_type', 'is_required', 'sequence')
    list_filter = ('question_type', 'is_required')
    search_fields = ('section__title', 'question_text')
    ordering = ['sequence']


@admin.register(FormInstance)
class FormInstanceAdmin(admin.ModelAdmin):
    list_display = ('template', 'completed_by', 'status', 'completed_at', 'created_at')
    list_filter = ('status', 'completed_at', 'context_type', 'created_at')
    search_fields = ('template__name', 'completed_by__username', 'context_id')
    ordering = ['-created_at']
    inlines = [FormResponseInline]


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ('instance', 'question', 'response_text', 'answered_at')
    list_filter = ('answered_at',)
    search_fields = ('instance__template__name', 'question__question_text')
    ordering = ['-answered_at']
