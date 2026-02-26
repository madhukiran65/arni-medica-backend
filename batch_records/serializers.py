from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    MasterBatchRecord,
    BatchRecord,
    BatchStep,
    BatchDeviation,
    BatchMaterial,
    BatchEquipment,
)


# ============================================================================
# MASTER BATCH RECORD SERIALIZERS
# ============================================================================

class MasterBatchRecordListSerializer(serializers.ModelSerializer):
    """List view serializer for MasterBatchRecord."""
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = MasterBatchRecord
        fields = [
            'id',
            'mbr_id',
            'title',
            'product_name',
            'product_code',
            'version',
            'status',
            'effective_date',
            'approved_by_name',
            'approval_date',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'mbr_id',
            'created_by_name',
            'approved_by_name',
            'created_at',
            'updated_at',
        ]


class MasterBatchRecordDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for MasterBatchRecord."""
    created_by = serializers.StringRelatedField(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
        allow_null=True
    )
    linked_document_title = serializers.CharField(
        source='linked_document.title',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = MasterBatchRecord
        fields = [
            'id',
            'mbr_id',
            'title',
            'product_name',
            'product_code',
            'version',
            'bill_of_materials',
            'manufacturing_instructions',
            'quality_specifications',
            'linked_document',
            'linked_document_title',
            'product_line',
            'product_line_name',
            'effective_date',
            'status',
            'approved_by',
            'approval_date',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'mbr_id',
            'created_by',
            'approved_by',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# BATCH STEP SERIALIZERS
# ============================================================================

class BatchStepListSerializer(serializers.ModelSerializer):
    """List view serializer for BatchStep."""
    operator_name = serializers.CharField(
        source='operator.get_full_name',
        read_only=True,
        allow_null=True
    )
    verifier_name = serializers.CharField(
        source='verifier.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BatchStep
        fields = [
            'id',
            'batch',
            'step_number',
            'instruction_text',
            'status',
            'is_within_spec',
            'operator_name',
            'operator_signed_at',
            'verifier_name',
            'verifier_signed_at',
            'started_at',
            'completed_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'operator_name',
            'verifier_name',
            'created_at',
        ]


class BatchStepDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for BatchStep."""
    operator = serializers.StringRelatedField(read_only=True)
    verifier = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BatchStep
        fields = [
            'id',
            'batch',
            'step_number',
            'instruction_text',
            'required_data_fields',
            'actual_values',
            'specifications',
            'status',
            'requires_verification',
            'operator',
            'operator_signed_at',
            'verifier',
            'verifier_signed_at',
            'deviation_notes',
            'started_at',
            'completed_at',
            'is_within_spec',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'operator',
            'verifier',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# BATCH DEVIATION SERIALIZERS
# ============================================================================

class BatchDeviationListSerializer(serializers.ModelSerializer):
    """List view serializer for BatchDeviation."""
    resolved_by_name = serializers.CharField(
        source='resolved_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BatchDeviation
        fields = [
            'id',
            'deviation_id',
            'batch',
            'deviation_type',
            'status',
            'description',
            'resolved_by_name',
            'resolution_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'deviation_id',
            'resolved_by_name',
            'created_at',
            'updated_at',
        ]


class BatchDeviationDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for BatchDeviation."""
    resolved_by = serializers.StringRelatedField(read_only=True)
    batch_step_number = serializers.CharField(
        source='batch_step.step_number',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BatchDeviation
        fields = [
            'id',
            'deviation_id',
            'batch',
            'batch_step',
            'batch_step_number',
            'deviation_type',
            'description',
            'impact_assessment',
            'immediate_action',
            'root_cause',
            'linked_deviation',
            'linked_capa',
            'status',
            'resolved_by',
            'resolution_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'deviation_id',
            'resolved_by',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# BATCH MATERIAL SERIALIZERS
# ============================================================================

class BatchMaterialListSerializer(serializers.ModelSerializer):
    """List view serializer for BatchMaterial."""
    dispensed_by_name = serializers.CharField(
        source='dispensed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    verified_by_name = serializers.CharField(
        source='verified_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BatchMaterial
        fields = [
            'id',
            'batch',
            'material_code',
            'material_name',
            'lot_number',
            'quantity_required',
            'quantity_used',
            'unit_of_measure',
            'status',
            'dispensed_by_name',
            'verified_by_name',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'dispensed_by_name',
            'verified_by_name',
            'created_at',
        ]


class BatchMaterialDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for BatchMaterial."""
    dispensed_by = serializers.StringRelatedField(read_only=True)
    verified_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BatchMaterial
        fields = [
            'id',
            'batch',
            'material_name',
            'material_code',
            'lot_number',
            'quantity_required',
            'quantity_used',
            'unit_of_measure',
            'status',
            'dispensed_by',
            'verified_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'dispensed_by',
            'verified_by',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# BATCH EQUIPMENT SERIALIZERS
# ============================================================================

class BatchEquipmentListSerializer(serializers.ModelSerializer):
    """List view serializer for BatchEquipment."""
    equipment_name_display = serializers.CharField(
        source='equipment.name',
        read_only=True,
        allow_null=True
    )
    verified_by_name = serializers.CharField(
        source='verified_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BatchEquipment
        fields = [
            'id',
            'batch',
            'equipment',
            'equipment_name',
            'equipment_name_display',
            'equipment_id_manual',
            'calibration_verified',
            'cleaning_verified',
            'verified_by_name',
            'usage_start',
            'usage_end',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'equipment_name_display',
            'verified_by_name',
            'created_at',
        ]


class BatchEquipmentDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for BatchEquipment."""
    verified_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = BatchEquipment
        fields = [
            'id',
            'batch',
            'equipment',
            'equipment_name',
            'equipment_id_manual',
            'usage_start',
            'usage_end',
            'calibration_verified',
            'cleaning_verified',
            'verified_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'verified_by',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# BATCH RECORD SERIALIZERS
# ============================================================================

class BatchRecordListSerializer(serializers.ModelSerializer):
    """List view serializer for BatchRecord."""
    mbr_title = serializers.CharField(
        source='mbr.title',
        read_only=True
    )
    site_name = serializers.CharField(
        source='site.name',
        read_only=True,
        allow_null=True
    )
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    released_by_name = serializers.CharField(
        source='released_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = BatchRecord
        fields = [
            'id',
            'batch_id',
            'batch_number',
            'lot_number',
            'mbr',
            'mbr_title',
            'quantity_planned',
            'quantity_produced',
            'quantity_rejected',
            'yield_percentage',
            'status',
            'production_line',
            'site_name',
            'has_deviations',
            'review_by_exception',
            'started_at',
            'completed_at',
            'reviewed_by_name',
            'released_by_name',
            'release_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'batch_id',
            'mbr_title',
            'site_name',
            'reviewed_by_name',
            'released_by_name',
            'created_at',
            'updated_at',
        ]


class BatchRecordDetailSerializer(serializers.ModelSerializer):
    """Detail view serializer for BatchRecord with nested data."""
    mbr_details = MasterBatchRecordListSerializer(
        source='mbr',
        read_only=True
    )
    reviewed_by = serializers.StringRelatedField(read_only=True)
    released_by = serializers.StringRelatedField(read_only=True)
    steps = BatchStepListSerializer(many=True, read_only=True)
    deviations = BatchDeviationListSerializer(many=True, read_only=True)
    materials = BatchMaterialListSerializer(many=True, read_only=True)
    equipment_usage = BatchEquipmentListSerializer(many=True, read_only=True)

    class Meta:
        model = BatchRecord
        fields = [
            'id',
            'batch_id',
            'batch_number',
            'lot_number',
            'mbr',
            'mbr_details',
            'quantity_planned',
            'quantity_produced',
            'quantity_rejected',
            'yield_percentage',
            'started_at',
            'completed_at',
            'status',
            'production_line',
            'site',
            'reviewed_by',
            'released_by',
            'release_date',
            'has_deviations',
            'review_by_exception',
            'steps',
            'deviations',
            'materials',
            'equipment_usage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'batch_id',
            'mbr_details',
            'reviewed_by',
            'released_by',
            'steps',
            'deviations',
            'materials',
            'equipment_usage',
            'created_at',
            'updated_at',
        ]


# ============================================================================
# WRITE SERIALIZERS FOR BATCH RECORD ACTIONS
# ============================================================================

class BatchRecordStartSerializer(serializers.Serializer):
    """Serializer for starting batch production."""
    pass


class BatchRecordCompleteSerializer(serializers.Serializer):
    """Serializer for completing batch production."""
    quantity_produced = serializers.IntegerField(min_value=0)
    quantity_rejected = serializers.IntegerField(min_value=0, required=False)


class BatchRecordReleaseSerializer(serializers.Serializer):
    """Serializer for releasing a batch."""
    pass


class BatchRecordRejectSerializer(serializers.Serializer):
    """Serializer for rejecting a batch."""
    pass


class BatchRecordQuarantineSerializer(serializers.Serializer):
    """Serializer for quarantining a batch."""
    pass


class BatchStepStartSerializer(serializers.Serializer):
    """Serializer for starting a batch step."""
    pass


class BatchStepCompleteSerializer(serializers.Serializer):
    """Serializer for completing a batch step."""
    actual_values = serializers.JSONField()


class BatchStepVerifySerializer(serializers.Serializer):
    """Serializer for verifying a batch step."""
    pass


class BatchStepSkipSerializer(serializers.Serializer):
    """Serializer for skipping a batch step."""
    pass


class BatchDeviationResolveSerializer(serializers.Serializer):
    """Serializer for resolving a deviation."""
    root_cause = serializers.CharField(required=False)
    immediate_action = serializers.CharField(required=False)


class BatchDeviationCloseSerializer(serializers.Serializer):
    """Serializer for closing a deviation."""
    pass


class BatchMaterialDispenseSerializer(serializers.Serializer):
    """Serializer for dispensing material."""
    pass


class BatchMaterialVerifySerializer(serializers.Serializer):
    """Serializer for verifying material."""
    pass


class BatchMaterialConsumeSerializer(serializers.Serializer):
    """Serializer for consuming material."""
    quantity_used = serializers.DecimalField(max_digits=12, decimal_places=3)


class BatchEquipmentStartUsageSerializer(serializers.Serializer):
    """Serializer for starting equipment usage."""
    pass


class BatchEquipmentEndUsageSerializer(serializers.Serializer):
    """Serializer for ending equipment usage."""
    pass


class BatchEquipmentVerifyCalibrationSerializer(serializers.Serializer):
    """Serializer for verifying equipment calibration."""
    pass


class BatchEquipmentVerifyCleaningSerializer(serializers.Serializer):
    """Serializer for verifying equipment cleaning."""
    pass


class MasterBatchRecordApproveSerializer(serializers.Serializer):
    """Serializer for approving a master batch record."""
    pass


class MasterBatchRecordSupersedSerializer(serializers.Serializer):
    """Serializer for superseding a master batch record."""
    pass


class MasterBatchRecordObsoleteSerializer(serializers.Serializer):
    """Serializer for marking master batch record as obsolete."""
    pass
