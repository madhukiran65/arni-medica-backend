from django.contrib import admin
from django.utils.html import format_html
from equipment.models import (
    Equipment,
    EquipmentQualification,
    CalibrationSchedule,
    CalibrationRecord,
    MaintenanceSchedule,
    MaintenanceRecord,
    EquipmentDocument,
)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        'equipment_id', 'name', 'equipment_type', 'status_badge',
        'criticality', 'serial_number', 'manufacturer', 'created_at'
    )
    list_filter = ('equipment_type', 'category', 'status', 'criticality', 'requires_calibration', 'requires_maintenance')
    search_fields = ('equipment_id', 'name', 'serial_number', 'manufacturer')
    readonly_fields = ('equipment_id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Identification', {
            'fields': ('equipment_id', 'name', 'description', 'serial_number', 'model_number')
        }),
        ('Classification', {
            'fields': ('equipment_type', 'category', 'manufacturer', 'qr_code')
        }),
        ('Location & Organization', {
            'fields': ('location', 'site', 'department')
        }),
        ('Status & Criticality', {
            'fields': ('status', 'criticality')
        }),
        ('Requirements', {
            'fields': ('requires_calibration', 'requires_maintenance')
        }),
        ('Dates', {
            'fields': ('purchase_date', 'installation_date', 'warranty_expiry')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'quarantined': 'orange',
            'out_of_service': 'red',
            'decommissioned': 'gray',
            'pending_qualification': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(EquipmentQualification)
class EquipmentQualificationAdmin(admin.ModelAdmin):
    list_display = (
        'qualification_id', 'equipment', 'qualification_type',
        'result_badge', 'status', 'execution_date'
    )
    list_filter = ('qualification_type', 'result', 'status', 'execution_date')
    search_fields = ('qualification_id', 'equipment__name', 'protocol_number')
    readonly_fields = ('qualification_id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Basic Information', {
            'fields': ('qualification_id', 'equipment', 'qualification_type', 'protocol_number')
        }),
        ('Files', {
            'fields': ('protocol_file', 'result_file'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('execution_date', 'result', 'deviations_noted')
        }),
        ('Personnel', {
            'fields': ('qualified_by', 'approved_by')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def result_badge(self, obj):
        colors = {
            'pass': 'green',
            'fail': 'red',
            'conditional': 'orange',
            'not_executed': 'gray',
        }
        color = colors.get(obj.result, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_result_display()
        )
    result_badge.short_description = 'Result'


@admin.register(CalibrationSchedule)
class CalibrationScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'equipment', 'interval_days', 'last_calibrated',
        'next_due_badge', 'auto_quarantine_on_overdue'
    )
    list_filter = ('auto_quarantine_on_overdue', 'interval_days')
    search_fields = ('equipment__name', 'equipment__equipment_id', 'reference_standards')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Equipment & Schedule', {
            'fields': ('equipment', 'interval_days', 'reminder_days_before')
        }),
        ('Calibration Details', {
            'fields': ('calibration_method', 'reference_standards', 'tolerance_specs')
        }),
        ('Dates', {
            'fields': ('last_calibrated', 'next_due')
        }),
        ('Administration', {
            'fields': ('auto_quarantine_on_overdue', 'responsible_person')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def next_due_badge(self, obj):
        from django.utils import timezone
        if obj.next_due:
            if timezone.now().date() > obj.next_due:
                color = 'red'
                status = 'OVERDUE'
            elif (obj.next_due - timezone.now().date()).days <= 30:
                color = 'orange'
                status = 'DUE SOON'
            else:
                color = 'green'
                status = 'OK'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} ({})</span>',
                color,
                obj.next_due,
                status
            )
        return '-'
    next_due_badge.short_description = 'Next Due'


@admin.register(CalibrationRecord)
class CalibrationRecordAdmin(admin.ModelAdmin):
    list_display = (
        'calibration_id', 'equipment', 'calibration_date',
        'result_badge', 'calibration_type', 'approved_by'
    )
    list_filter = ('result', 'calibration_type', 'calibration_date')
    search_fields = ('calibration_id', 'equipment__name', 'certificate_number')
    readonly_fields = ('calibration_id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Basic Information', {
            'fields': ('calibration_id', 'equipment', 'calibration_date', 'calibration_type')
        }),
        ('Calibration Data', {
            'fields': ('as_found_data', 'as_left_data')
        }),
        ('Results', {
            'fields': ('result', 'certificate_number', 'certificate_file')
        }),
        ('Personnel', {
            'fields': ('performed_by_internal', 'performed_by_vendor', 'approved_by')
        }),
        ('Additional', {
            'fields': ('notes', 'linked_deviation'),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def result_badge(self, obj):
        colors = {
            'pass': 'green',
            'fail': 'red',
            'adjusted_pass': 'blue',
            'out_of_tolerance': 'orange',
        }
        color = colors.get(obj.result, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_result_display()
        )
    result_badge.short_description = 'Result'


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'equipment', 'maintenance_type', 'interval_days',
        'last_performed', 'next_due_badge', 'responsible_person'
    )
    list_filter = ('maintenance_type', 'interval_days')
    search_fields = ('equipment__name', 'equipment__equipment_id', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Equipment & Type', {
            'fields': ('equipment', 'maintenance_type', 'interval_days')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Schedule', {
            'fields': ('last_performed', 'next_due', 'responsible_person')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def next_due_badge(self, obj):
        from django.utils import timezone
        if obj.next_due:
            if timezone.now().date() > obj.next_due:
                color = 'red'
                status = 'OVERDUE'
            else:
                color = 'green'
                status = 'OK'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} ({})</span>',
                color,
                obj.next_due,
                status
            )
        return '-'
    next_due_badge.short_description = 'Next Due'


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'maintenance_id', 'equipment', 'maintenance_date',
        'maintenance_type', 'status_badge', 'performed_by', 'downtime_hours'
    )
    list_filter = ('maintenance_type', 'status', 'maintenance_date')
    search_fields = ('maintenance_id', 'equipment__name', 'description')
    readonly_fields = ('maintenance_id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Basic Information', {
            'fields': ('maintenance_id', 'equipment', 'maintenance_date', 'maintenance_type')
        }),
        ('Work Details', {
            'fields': ('description', 'work_performed', 'parts_replaced', 'downtime_hours')
        }),
        ('Personnel & Status', {
            'fields': ('performed_by', 'status')
        }),
        ('Additional', {
            'fields': ('linked_deviation',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'scheduled': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(EquipmentDocument)
class EquipmentDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'equipment', 'document_type',
        'expiry_badge', 'uploaded_by', 'created_at'
    )
    list_filter = ('document_type', 'expiry_date', 'created_at')
    search_fields = ('title', 'equipment__name', 'equipment__equipment_id')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Document Information', {
            'fields': ('equipment', 'document_type', 'title')
        }),
        ('File & Expiry', {
            'fields': ('file', 'expiry_date')
        }),
        ('Audit Trail', {
            'fields': ('uploaded_by', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def expiry_badge(self, obj):
        from django.utils import timezone
        if obj.expiry_date:
            if timezone.now().date() > obj.expiry_date:
                color = 'red'
                status = 'EXPIRED'
            elif (obj.expiry_date - timezone.now().date()).days <= 30:
                color = 'orange'
                status = 'EXPIRING SOON'
            else:
                color = 'green'
                status = 'VALID'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} ({})</span>',
                color,
                obj.expiry_date,
                status
            )
        return 'No Expiry'
    expiry_badge.short_description = 'Expiry Status'
