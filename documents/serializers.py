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
    DocumentCollaborator,
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
            'checkout_reason',
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
            'is_final_approver',
        ]
        read_only_fields = ['id', 'approved_at']


class DocumentCollaboratorSerializer(serializers.ModelSerializer):
    """Serializer for DocumentCollaborator with user and department details."""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    department = serializers.SerializerMethodField()

    class Meta:
        model = DocumentCollaborator
        fields = [
            'id', 'document', 'user_id', 'username', 'full_name',
            'email', 'department', 'roles', 'status', 'added_by',
            'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_by', 'added_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_department(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and profile.department:
            return profile.department.name
        return ''


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
            'legacy_document_id',
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
            'legacy_document_id',
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
    # User detail fields for Created By / Updated By display
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        default=None
    )
    created_by_name = serializers.SerializerMethodField()
    updated_by_username = serializers.CharField(
        source='updated_by.username',
        read_only=True,
        default=None
    )
    updated_by_name = serializers.SerializerMethodField()
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
            'legacy_document_id',
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
            'training_completion_required',
            'training_completion_deadline_days',
            'training_completed_date',
            'approved_date',
            'cancelled_date',
            'cancelled_by',
            'cancellation_reason',
            'superseded_by',
            'workflow_category',
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
            'watermark_text',
            'review_frequency_days',
            'requires_dual_approval',
            'content',
            'content_html',
            'content_plain_text',
            'description',
            'custom_fields',
            'versions',
            'approvers',
            'current_checkout',
            'approval_status',
            'created_at',
            'created_by',
            'created_by_username',
            'created_by_name',
            'updated_at',
            'updated_by',
            'updated_by_username',
            'updated_by_name',
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
            'created_by_username',
            'created_by_name',
            'updated_by_username',
            'updated_by_name',
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

    def get_created_by_name(self, obj):
        """Return full name of the creator."""
        if obj.created_by:
            name = f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
            return name or obj.created_by.username
        return None

    def get_updated_by_name(self, obj):
        """Return full name of the last updater."""
        if obj.updated_by:
            name = f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
            return name or obj.updated_by.username
        return None

    def get_current_checkout(self, obj):
        """Get the current active checkout if exists."""
        checkout = obj.get_active_checkout()
        if checkout:
            return DocumentCheckoutSerializer(checkout).data
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
            'legacy_document_id',
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
            'training_completion_required',
            'training_completion_deadline_days',
            'workflow_category',
            'content',
            'content_html',
            'description',
            'custom_fields',
        ]
    
    def create(self, validated_data):
        """Create new document and auto-generate document ID."""
        document = Document(**validated_data)
        document.save()
        return document


# ============================================================================
# DOCUMENT COMMENT SERIALIZERS
# ============================================================================

class DocumentCommentSerializer(serializers.ModelSerializer):
    """Full comment serializer with author info and replies."""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_name = serializers.SerializerMethodField()
    resolved_by_username = serializers.CharField(
        source='resolved_by.username', read_only=True, default=None
    )
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        from .models import DocumentComment
        model = DocumentComment
        fields = [
            'id', 'document', 'parent', 'author', 'author_username', 'author_name',
            'text', 'comment_type', 'selection_from', 'selection_to', 'quoted_text',
            'status', 'resolved_by', 'resolved_by_username', 'resolved_at',
            'document_version', 'replies', 'reply_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'author', 'author_username', 'author_name',
            'resolved_by', 'resolved_by_username', 'resolved_at',
            'document_version', 'replies', 'reply_count',
            'created_at', 'updated_at',
        ]

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username

    def get_replies(self, obj):
        if obj.parent is not None:
            return []  # Don't nest infinitely
        replies = obj.replies.select_related('author', 'resolved_by').order_by('created_at')
        return DocumentCommentSerializer(replies, many=True).data

    def get_reply_count(self, obj):
        return obj.replies.count()


class DocumentSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for track changes / suggestions."""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_name = serializers.SerializerMethodField()
    reviewed_by_username = serializers.CharField(
        source='reviewed_by.username', read_only=True, default=None
    )

    class Meta:
        from .models import DocumentSuggestion
        model = DocumentSuggestion
        fields = [
            'id', 'document', 'author', 'author_username', 'author_name',
            'suggestion_type', 'selection_from', 'selection_to',
            'original_text', 'suggested_text', 'reason',
            'status', 'reviewed_by', 'reviewed_by_username', 'reviewed_at',
            'document_version', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'document', 'author', 'author_username', 'author_name',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at',
            'document_version', 'created_at', 'updated_at',
        ]

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username


class DocumentContentUpdateSerializer(serializers.Serializer):
    """Serializer for saving document content from the TipTap editor."""
    content = serializers.JSONField(required=True, help_text="TipTap ProseMirror JSON")
    content_html = serializers.CharField(required=False, default='', help_text="Rendered HTML")
    editor_metadata = serializers.JSONField(required=False, default=dict, help_text="Editor UI state metadata")
    header_content = serializers.CharField(required=False, default='', help_text="Header HTML content")
    footer_content = serializers.CharField(required=False, default='', help_text="Footer HTML content")
    page_color = serializers.CharField(required=False, default='', max_length=20, help_text="Page background color")
    columns_count = serializers.IntegerField(required=False, default=1, help_text="Number of columns")
    theme_id = serializers.CharField(required=False, default='office', max_length=50, help_text="Theme identifier")
    watermark_text = serializers.CharField(required=False, default='', allow_blank=True, max_length=200, help_text="Watermark text")


# ============================================================================
# ACTION SERIALIZERS
# ============================================================================

class CheckoutActionSerializer(serializers.Serializer):
    """Serializer for document checkout action."""
    
    checkout_reason = serializers.CharField(
        max_length=500,
        required=False,
        default=''
    )
    expected_checkin_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None
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
