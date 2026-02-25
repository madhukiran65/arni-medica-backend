from django.contrib import admin
from .models import (
    Supplier, SupplierEvaluation, SupplierDocument, SupplierCorrectiveAction
)


class SupplierEvaluationInline(admin.TabularInline):
    model = SupplierEvaluation
    fields = ('evaluation_type', 'overall_score', 'recommendation')
    extra = 0


class SupplierDocumentInline(admin.TabularInline):
    model = SupplierDocument
    fields = ('document_type', 'title', 'uploaded_by', 'uploaded_at')
    extra = 0


class SupplierCorrectiveActionInline(admin.TabularInline):
    model = SupplierCorrectiveAction
    fields = ('issue_description', 'scar_number', 'status')
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_id', 'name', 'supplier_type', 'qualification_status', 'risk_level')
    list_filter = ('supplier_type', 'qualification_status', 'risk_level', 'iso_certified', 'gmp_compliant', 'created_at')
    search_fields = ('supplier_id', 'name', 'contact_name', 'city')
    ordering = ['-created_at']
    inlines = [SupplierEvaluationInline, SupplierDocumentInline, SupplierCorrectiveActionInline]


@admin.register(SupplierEvaluation)
class SupplierEvaluationAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'evaluation_type', 'overall_score', 'recommendation', 'created_at')
    list_filter = ('evaluation_type', 'recommendation', 'created_at')
    search_fields = ('supplier__supplier_id', 'supplier__name')
    ordering = ['-created_at']


@admin.register(SupplierDocument)
class SupplierDocumentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'document_type', 'title', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('supplier__supplier_id', 'title')
    ordering = ['-uploaded_at']


@admin.register(SupplierCorrectiveAction)
class SupplierCorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'scar_number', 'status', 'issue_description')
    list_filter = ('status', 'created_at')
    search_fields = ('supplier__supplier_id', 'scar_number', 'issue_description')
    ordering = ['-created_at']
