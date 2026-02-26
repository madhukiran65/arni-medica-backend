from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    MasterBatchRecord,
    BatchRecord,
    BatchStep,
    BatchDeviation,
    BatchMaterial,
    BatchEquipment,
)


@admin.register(MasterBatchRecord)
class MasterBatchRecordAdmin(admin.ModelAdmin):
    """Admin interface for MasterBatchRecord."""

    list_display = [
        'mbr_id',
        'title',
        'product_code',
        'version',
        'status_badge',
        'product_line',
        'effective_date',
        'created_at',
    ]
    list_filter = [
        'status',
        'product_line',
        'created_at',
        'approval_date',
    ]
    search_fields = [
        'mbr_id',
        'title',
        'product_name',
        'product_code',
    ]
    readonly_fields = [
        'mbr_id',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('mbr_id', 'title', 'product_name', 'product_code')
        }),
        ('Details', {
            'fields': (
                'version',
                'effective_date',
                'product_line',
                'linked_document',
            )
        }),
        ('Content', {
            'fields': (
                'bill_of_materials',
                'manufacturing_instructions',
                'quality_specifications',
            ),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': (
                'status',
                'approved_by',
                'approval_date',
            )
        }),
        ('System', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'draft': '#FFA500',
            'in_review': '#3498db',
            'approved': '#27ae60',
            'superseded': '#95a5a6',
            'obsolete': '#e74c3c',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def get_readonly_fields(self, request, obj=None):
        """Make mbr_id always readonly."""
        readonly = list(self.readonly_fields)
        if obj:
            readonly.extend(['title', 'product_name', 'product_code'])
        return readonly


@admin.register(BatchRecord)
class BatchRecordAdmin(admin.ModelAdmin):
    """Admin interface for BatchRecord."""

    list_display = [
        'batch_id',
        'batch_number',
        'lot_number',
        'mbr_link',
        'status_badge',
        'quantity_produced',
        'yield_percentage',
        'has_deviations_badge',
        'started_at',
    ]
    list_filter = [
        'status',
        'site',
        'has_deviations',
        'review_by_exception',
        'created_at',
        'started_at',
        'completed_at',
    ]
    search_fields = [
        'batch_id',
        'batch_number',
        'lot_number',
        'mbr__mbr_id',
    ]
    readonly_fields = [
        'batch_id',
        'yield_percentage',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('batch_id', 'batch_number', 'lot_number', 'mbr')
        }),
        ('Production', {
            'fields': (
                'quantity_planned',
                'quantity_produced',
                'quantity_rejected',
                'yield_percentage',
                'started_at',
                'completed_at',
            )
        }),
        ('Details', {
            'fields': (
                'production_line',
                'site',
                'status',
            )
        }),
        ('Review & Release', {
            'fields': (
                'reviewed_by',
                'released_by',
                'release_date',
                'has_deviations',
                'review_by_exception',
            )
        }),
        ('System', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def mbr_link(self, obj):
        """Link to related MasterBatchRecord."""
        url = reverse(
            'admin:batch_records_masterbatchrecord_change',
            args=[obj.mbr.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.mbr.mbr_id
        )

    mbr_link.short_description = 'Master Batch Record'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': '#95a5a6',
            'in_progress': '#3498db',
            'completed': '#f39c12',
            'under_review': '#9b59b6',
            'released': '#27ae60',
            'rejected': '#e74c3c',
            'quarantined': '#c0392b',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def has_deviations_badge(self, obj):
        """Display deviation status."""
        if obj.has_deviations:
            return format_html(
                '<span style="background-color: #e74c3c; color: white; '
                'padding: 3px 8px; border-radius: 3px;">Has Deviations</span>'
            )
        return format_html(
            '<span style="background-color: #27ae60; color: white; '
            'padding: 3px 8px; border-radius: 3px;">No Deviations</span>'
        )

    has_deviations_badge.short_description = 'Deviations'


class BatchStepInline(admin.TabularInline):
    """Inline admin for BatchStep."""
    model = BatchStep
    extra = 0
    fields = [
        'step_number',
        'status',
        'operator',
        'is_within_spec',
        'completed_at',
    ]
    readonly_fields = ['step_number', 'operator']


class BatchMaterialInline(admin.TabularInline):
    """Inline admin for BatchMaterial."""
    model = BatchMaterial
    extra = 0
    fields = [
        'material_code',
        'lot_number',
        'quantity_required',
        'quantity_used',
        'status',
    ]


class BatchEquipmentInline(admin.TabularInline):
    """Inline admin for BatchEquipment."""
    model = BatchEquipment
    extra = 0
    fields = [
        'equipment_name',
        'calibration_verified',
        'cleaning_verified',
        'usage_start',
        'usage_end',
    ]


@admin.register(BatchStep)
class BatchStepAdmin(admin.ModelAdmin):
    """Admin interface for BatchStep."""

    list_display = [
        'batch_link',
        'step_number',
        'status_badge',
        'operator_name',
        'is_within_spec_badge',
        'requires_verification',
        'completed_at',
    ]
    list_filter = [
        'status',
        'is_within_spec',
        'requires_verification',
        'created_at',
    ]
    search_fields = [
        'batch__batch_id',
        'instruction_text',
    ]
    readonly_fields = [
        'operator',
        'verifier',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('batch', 'step_number')
        }),
        ('Instructions', {
            'fields': ('instruction_text', 'required_data_fields')
        }),
        ('Data Collection', {
            'fields': (
                'actual_values',
                'specifications',
                'is_within_spec',
            )
        }),
        ('Execution', {
            'fields': (
                'status',
                'operator',
                'operator_signed_at',
                'started_at',
                'completed_at',
            )
        }),
        ('Verification', {
            'fields': (
                'requires_verification',
                'verifier',
                'verifier_signed_at',
                'deviation_notes',
            )
        }),
        ('System', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def batch_link(self, obj):
        """Link to related BatchRecord."""
        url = reverse(
            'admin:batch_records_batchrecord_change',
            args=[obj.batch.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.batch.batch_id
        )

    batch_link.short_description = 'Batch Record'

    def operator_name(self, obj):
        """Display operator name."""
        return obj.operator.get_full_name() if obj.operator else '-'

    operator_name.short_description = 'Operator'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': '#95a5a6',
            'in_progress': '#3498db',
            'completed': '#27ae60',
            'skipped': '#f39c12',
            'deviated': '#e74c3c',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def is_within_spec_badge(self, obj):
        """Display spec compliance."""
        if obj.is_within_spec:
            return format_html(
                '<span style="color: #27ae60;">✓ Within Spec</span>'
            )
        return format_html(
            '<span style="color: #e74c3c;">✗ Out of Spec</span>'
        )

    is_within_spec_badge.short_description = 'Spec Compliance'


@admin.register(BatchDeviation)
class BatchDeviationAdmin(admin.ModelAdmin):
    """Admin interface for BatchDeviation."""

    list_display = [
        'deviation_id',
        'batch_link',
        'deviation_type_badge',
        'status_badge',
        'resolved_by_name',
        'created_at',
    ]
    list_filter = [
        'deviation_type',
        'status',
        'created_at',
        'resolution_date',
    ]
    search_fields = [
        'deviation_id',
        'description',
        'batch__batch_id',
    ]
    readonly_fields = [
        'deviation_id',
        'resolved_by',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    ]
    fieldsets = (
        ('Identification', {
            'fields': ('deviation_id', 'batch', 'batch_step')
        }),
        ('Details', {
            'fields': (
                'deviation_type',
                'description',
                'impact_assessment',
            )
        }),
        ('Actions', {
            'fields': (
                'immediate_action',
                'root_cause',
            )
        }),
        ('Linking', {
            'fields': (
                'linked_deviation',
                'linked_capa',
            )
        }),
        ('Resolution', {
            'fields': (
                'status',
                'resolved_by',
                'resolution_date',
            )
        }),
        ('System', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def batch_link(self, obj):
        """Link to related BatchRecord."""
        url = reverse(
            'admin:batch_records_batchrecord_change',
            args=[obj.batch.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.batch.batch_id
        )

    batch_link.short_description = 'Batch Record'

    def deviation_type_badge(self, obj):
        """Display deviation type as a badge."""
        colors = {
            'parameter_excursion': '#3498db',
            'equipment_failure': '#e74c3c',
            'material_issue': '#f39c12',
            'process_deviation': '#9b59b6',
            'documentation_error': '#1abc9c',
            'environmental': '#16a085',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.deviation_type, '#95a5a6'),
            obj.get_deviation_type_display()
        )

    deviation_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'open': '#e74c3c',
            'investigating': '#f39c12',
            'resolved': '#27ae60',
            'closed': '#95a5a6',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def resolved_by_name(self, obj):
        """Display resolver name."""
        return (
            obj.resolved_by.get_full_name() if obj.resolved_by else '-'
        )

    resolved_by_name.short_description = 'Resolved By'


@admin.register(BatchMaterial)
class BatchMaterialAdmin(admin.ModelAdmin):
    """Admin interface for BatchMaterial."""

    list_display = [
        'batch_link',
        'material_code',
        'lot_number',
        'quantity_required',
        'quantity_used',
        'status_badge',
        'dispensed_by_name',
    ]
    list_filter = [
        'status',
        'created_at',
    ]
    search_fields = [
        'batch__batch_id',
        'material_code',
        'material_name',
        'lot_number',
    ]
    readonly_fields = [
        'dispensed_by',
        'verified_by',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    ]
    fieldsets = (
        ('Batch', {
            'fields': ('batch',)
        }),
        ('Material Details', {
            'fields': (
                'material_name',
                'material_code',
                'lot_number',
            )
        }),
        ('Quantity', {
            'fields': (
                'quantity_required',
                'quantity_used',
                'unit_of_measure',
            )
        }),
        ('Status & Approvals', {
            'fields': (
                'status',
                'dispensed_by',
                'verified_by',
            )
        }),
        ('System', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def batch_link(self, obj):
        """Link to related BatchRecord."""
        url = reverse(
            'admin:batch_records_batchrecord_change',
            args=[obj.batch.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.batch.batch_id
        )

    batch_link.short_description = 'Batch Record'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': '#95a5a6',
            'dispensed': '#3498db',
            'verified': '#f39c12',
            'consumed': '#27ae60',
            'returned': '#e74c3c',
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95a5a6'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def dispensed_by_name(self, obj):
        """Display dispenser name."""
        return (
            obj.dispensed_by.get_full_name() if obj.dispensed_by else '-'
        )

    dispensed_by_name.short_description = 'Dispensed By'


@admin.register(BatchEquipment)
class BatchEquipmentAdmin(admin.ModelAdmin):
    """Admin interface for BatchEquipment."""

    list_display = [
        'batch_link',
        'equipment_name',
        'equipment_id_manual',
        'calibration_verified_badge',
        'cleaning_verified_badge',
        'usage_start',
        'usage_end',
    ]
    list_filter = [
        'calibration_verified',
        'cleaning_verified',
        'created_at',
    ]
    search_fields = [
        'batch__batch_id',
        'equipment_name',
        'equipment_id_manual',
    ]
    readonly_fields = [
        'verified_by',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    ]
    fieldsets = (
        ('Batch', {
            'fields': ('batch',)
        }),
        ('Equipment', {
            'fields': (
                'equipment',
                'equipment_name',
                'equipment_id_manual',
            )
        }),
        ('Usage', {
            'fields': (
                'usage_start',
                'usage_end',
            )
        }),
        ('Verification', {
            'fields': (
                'calibration_verified',
                'cleaning_verified',
                'verified_by',
            )
        }),
        ('System', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def batch_link(self, obj):
        """Link to related BatchRecord."""
        url = reverse(
            'admin:batch_records_batchrecord_change',
            args=[obj.batch.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.batch.batch_id
        )

    batch_link.short_description = 'Batch Record'

    def calibration_verified_badge(self, obj):
        """Display calibration status."""
        if obj.calibration_verified:
            return format_html(
                '<span style="color: #27ae60;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: #95a5a6;">✗ Not Verified</span>'
        )

    calibration_verified_badge.short_description = 'Calibration'

    def cleaning_verified_badge(self, obj):
        """Display cleaning status."""
        if obj.cleaning_verified:
            return format_html(
                '<span style="color: #27ae60;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: #95a5a6;">✗ Not Verified</span>'
        )

    cleaning_verified_badge.short_description = 'Cleaning'
