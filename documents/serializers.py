"""
Document Control Module Serializers

Comprehensive DRF serializers for document management including:
- Document type and subtype serialization
- Checkout and approval workflows
- Version control and snapshots
- Change order and approval management
- Lifecycle transitions and validation
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    DocumentInfocardType,
    DocumentSubType,
    DocumentCheckout,
    DocumentApprover,
    DocumentSnapshot,
    DocumentVersion,
    DocumentChangeOrder,
    DocumentChangeApproval,
    Document,
)


# ============================================================================
# DOCUMENT TYPE SERIALIZERS
# ============================================================================

class DocumentInfocardTypeSerializer(serializers.ModelSerializer):
    """Serializer for DocumentInfocardType with all fields."""
    
    class Meta:
        model = DocumentInfocardType
        fields = [
            'id',
            'name',
            'prefix',
            'description',
            'is_active',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'updated_at', 'updated_by']


class DocumentSubTypeSerializer(serializers.ModelSerializer):
    """Serializer for DocumentSubType with read-only infocard type name."""
    
    infocard_type_name = serializers.CharField(
        source='infocard_type.name',
        read_only=True
    )
    
    class Meta:
        model = DocumentSubType
        fields = [
            'id',
            'infocard_type',
            'infocard_type_name',
            'name',
            'description',
            'is_active',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'updated_at', 'updated_by']


# ============================================================================
# CHECKOUT & APPROVER SERIALIZERS
# ============================================================================

class DocumentCheckoutSerializer(serializers.ModelSerializer):
    """Serializer for DocumentCheckout with read-only checked out by username."""
    
    checked_out_by_username = serializers.CharField(
        source='checked_out_by.username',
        read_only=True
    )
    
    class Meta:
        model = DocumentCheckout
        fields = [
            'id',
            'document',
            'checked_out_by',
            'checked_out_by_username',
            'checked_out_at',
            'expected_checkin_date',
            'is_active',
            'reason',
        ]
        read_only_fields = ['id', 'checked_out_at']


class DocumentApproverSerializer(serializers.ModelSerializer):
    """Serializer for DocumentApprover with read-only approver username."""
    
    approver_username = serializers.CharField(
        source='approver.username',
        read_only=True
    )
    
    class Meta:
        model = DocumentApprover
        fields = [
            'id',
            'document',
            'approver',
            'approver_username',
            'approval_status',
            'role_required',
            'sequence',
            'comments',
            'approved_at',
            'signature',
        ]
        read_only_fields = ['id', 'approved_at']


# ============================================================================
# SNAPSHOT & VERSION SERIALIZERS
# ============================================================================

class DocumentSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for DocumentSnapshot with read-only immutable fields."""

    class Meta:
        model = DocumentSnapshot
        fields = [
            'id',
            'document',
            'version_string',
            'snapshot_type',
            'snapshot_data',
            'created_at',
            'created_by',
        ]
        read_only_fields = fields


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentVersion with computed version string."""

    version_string = serializers.SerializerMethodField()

    class Meta:
        model = DocumentVersion
        fields = [
            'id',
            'document',
            'major_version',
            'minor_version',
            'version_string',
            'change_type',
            'is_major_change',
            'change_summary',
            'snapshot_data',
            'released_date',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'updated_at', 'updated_by']

    def get_version_string(self, obj):
        """Return formatted version string like '2.1'."""
        return f"{obj.major_version}.{obj.minor_version}"


# ============================================================================
# CHANGE ORDER & APPROVAL SERIALIZERS
# ============================================================================

class DocumentChangeOrderSerializer(serializers.ModelSerializer):
    """Serializer for DocumentChangeOrder."""

    class Meta:
        model = DocumentChangeOrder
        fields = [
            'id',
            'document',
            'change_number',
            'title',
            'description',
            'reason_for_change',
            'proposed_by',
            'status',
            'impact_assessment',
            'regulatory_impact',
            'training_impact',
            'affected_processes',
            'implementation_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentChangeApprovalSerializer(serializers.ModelSerializer):
    """Serializer for DocumentChangeApproval."""

    class Meta:
        model = DocumentChangeApproval
        fields = [
            'id',
            'change_order',
            'approver',
            'status',
            'comments',
            'approved_at',
        ]
        read_only_fields = ['id', 'responded_at']


# ============================================================================
# DOCUMENT SERIALIZERS
# ============================================================================

class DocumentListSerializer(serializers.ModelSerializer):
    """Compact serializer for document lists."""

    infocard_type_name = serializers.CharField(
        source='infocard_type.name',
        read_only=True
    )
    version_string = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        default=None
    )
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True,
        default=None
    )
    
    class Meta:
        model = Document
        fields = [
            'id',
            'document_id',
            'title',
            'infocard_type',
            'infocard_type_name',
            'vault_state',
            'lifecycle_stage',
            'version_string',
            'department',
            'department_name',
            'owner',
            'owner_username',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'document_id',
            'version_string',
            'infocard_type_name',
            'department_name',
            'owner_username',
            'created_at',
        ]
    
    def get_version_string(self, obj):
        """Return formatted version string like '2.1'."""
        return f"{obj.major_version}.{obj.minor_version}"


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Full document serializer with nested relationships."""
    
    infocard_type_name = serializers.CharField(
        source='infocard_type.name',
        read_only=True
    )
    subtype_name = serializers.CharField(
        source='subtype.name',
        read_only=True,
        default=None
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        default=None
    )
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True,
        default=None
    )
    locked_by_username = serializers.CharField(
        source='locked_by.username',
        read_only=True,
        default=None
    )
    version_string = serializers.SerializerMethodField()
    versions = DocumentVersionSerializer(
        many=True,
        read_only=True
    )
    approvers = DocumentApproverSerializer(
        many=True,
        read_only=True
    )
    current_checkout = serializers.SerializerMethodField()
    approval_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'document_id',
            'title',
            'abbreviation',
            'infocard_type',
            'infocard_type_name',
            'subtype',
            'subtype_name',
            'department',
            'department_name',
            'owner',
            'owner_username',
            'business_unit',
            'site',
            'major_version',
            'minor_version',
            'version_string',
            'revision_number',
            'previous_version',
            'change_summary',
            'vault_state',
            'lifecycle_stage',
            'is_locked',
            'locked_by',
            'locked_by_username',
            'locked_at',
            'lock_reason',
            'effective_date',
            'next_review_date',
            'last_reviewed_date',
            'released_date',
            'obsolete_date',
            'archived_date',
            'review_period_months',
            'file',
            'file_hash',
            'file_size',
            'file_type',
            'original_filename',
            'external_file_url',
            'regulatory_requirement',
            'requires_training',
            'training_applicable_roles',
            'distribution_restriction',
            'confidentiality_level',
            'subject_keywords',
            'ai_classification',
            'ai_confidence',
            'ai_classification_date',
            'requires_approval',
            'is_template',
            'is_controlled_copy',
            'has_attachments',
            'custom_fields',
            'versions',
            'approvers',
            'current_checkout',
            'approval_status',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'document_id',
            'version_string',
            'infocard_type_name',
            'subtype_name',
            'department_name',
            'owner_username',
            'locked_by_username',
            'versions',
            'approvers',
            'current_checkout',
            'approval_status',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
    
    def get_version_string(self, obj):
        """Return formatted version string like '2.1'."""
        return f"{obj.major_version}.{obj.minor_version}"
    
    def get_current_checkout(self, obj):
        """Get the current active checkout if exists."""
        try:
            checkout = obj.active_checkout
            if checkout and checkout.is_active:
                return DocumentCheckoutSerializer(checkout).data
        except DocumentCheckout.DoesNotExist:
            pass
        return None
    
    def get_approval_status(self, obj):
        """Get approval status summary."""
        return obj.get_approval_status()


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new documents."""
    
    class Meta:
        model = Document
        fields = [
            'title',
            'abbreviation',
            'infocard_type',
            'subtype',
            'department',
            'owner',
            'business_unit',
            'site',
            'file',
            'regulatory_requirement',
            'requires_training',
            'training_applicable_roles',
            'distribution_restriction',
            'confidentiality_level',
            'subject_keywords',
            'requires_approval',
            'is_template',
            'review_period_months',
            'custom_fields',
        ]
    
    def create(self, validated_data):
        """Create new document and auto-generate document ID."""
        document = Document(**validated_data)
        document.save()
        return document


# ============================================================================
# ACTION SERIALIZERS
# ============================================================================

class CheckoutActionSerializer(serializers.Serializer):
    """Serializer for document checkout action."""
    
    checkout_reason = serializers.CharField(
        max_length=500,
        required=True
    )
    expected_checkin_date = serializers.DateTimeField(
        required=True
    )


class CheckinActionSerializer(serializers.Serializer):
    """Serializer for document check-in action."""
    
    file = serializers.FileField(required=False)
    change_summary = serializers.CharField(
        max_length=1000,
        required=True
    )
    is_major_change = serializers.BooleanField(
        default=False
    )


class LifecycleTransitionSerializer(serializers.Serializer):
    """Serializer for document lifecycle state transitions."""
    
    target_stage = serializers.CharField(
        max_length=50,
        required=True
    )
    comments = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
    password = serializers.CharField(
        max_length=255,
        required=True,
        help_text="User password for electronic signature"
    )
