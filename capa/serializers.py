"""
CAPA (Corrective and Preventive Actions) Module Serializers

Comprehensive DRF serializers for CAPA management including:
- CAPA lifecycle and phase tracking
- Approval workflows and responses
- Risk matrix and 5W analysis
- Document attachment and comment management
- Extension request handling
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    CAPA,
    CAPAApproval,
    CAPADocument,
    CAPAComment,
)


# ============================================================================
# CAPA SERIALIZERS
# ============================================================================

class CAPAListSerializer(serializers.ModelSerializer):
    """Compact serializer for CAPA lists."""
    
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True,
        allow_null=True
    )
    risk_priority_number = serializers.SerializerMethodField()
    
    class Meta:
        model = CAPA
        fields = [
            'id',
            'capa_id',
            'title',
            'current_phase',
            'priority',
            'category',
            'capa_type',
            'department',
            'department_name',
            'assigned_to',
            'assigned_to_username',
            'target_completion_date',
            'risk_priority_number',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'capa_id',
            'risk_priority_number',
            'department_name',
            'assigned_to_username',
            'created_at',
        ]
    
    def get_risk_priority_number(self, obj):
        """Calculate and return risk priority number."""
        return obj.risk_priority_number


class CAPADetailSerializer(serializers.ModelSerializer):
    """Full CAPA serializer with nested relationships."""
    
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True,
        allow_null=True
    )
    responsible_person_username = serializers.CharField(
        source='responsible_person.username',
        read_only=True,
        allow_null=True
    )
    coordinator_username = serializers.CharField(
        source='coordinator.username',
        read_only=True,
        allow_null=True
    )
    closed_by_username = serializers.CharField(
        source='closed_by.username',
        read_only=True,
        allow_null=True
    )
    root_cause_verified_by_username = serializers.CharField(
        source='root_cause_verified_by.username',
        read_only=True,
        allow_null=True
    )
    implementation_verified_by_username = serializers.CharField(
        source='implementation_verified_by.username',
        read_only=True,
        allow_null=True
    )
    effectiveness_verified_by_username = serializers.CharField(
        source='effectiveness_verified_by.username',
        read_only=True,
        allow_null=True
    )
    extension_approved_by_username = serializers.CharField(
        source='extension_approved_by.username',
        read_only=True,
        allow_null=True
    )
    risk_priority_number = serializers.SerializerMethodField()
    approvals = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = CAPA
        fields = [
            'id',
            'capa_id',
            'title',
            'description',
            'source',
            'source_reference',
            'complaint',
            'audit_finding',
            'deviation',
            'category',
            'priority',
            'capa_type',
            'current_phase',
            'phase_entered_at',
            'what_happened',
            'when_happened',
            'where_happened',
            'who_affected',
            'why_happened',
            'how_discovered',
            'root_cause_analysis_method',
            'root_cause',
            'contributing_factors',
            'root_cause_verified',
            'root_cause_verified_by',
            'root_cause_verified_by_username',
            'root_cause_verified_date',
            'risk_severity',
            'risk_occurrence',
            'risk_detection',
            'risk_acceptability',
            'pre_action_rpn',
            'post_action_rpn',
            'risk_priority_number',
            'planned_actions',
            'responsible_person',
            'responsible_person_username',
            'target_completion_date',
            'actual_completion_date',
            'implementation_notes',
            'implementation_evidence',
            'implementation_verified',
            'implementation_verified_by',
            'implementation_verified_by_username',
            'effectiveness_criteria',
            'effectiveness_check_date',
            'effectiveness_result',
            'effectiveness_evidence',
            'effectiveness_verified_by',
            'effectiveness_verified_by_username',
            'has_extension',
            'extension_requested_date',
            'extension_reason',
            'extension_new_due_date',
            'extension_approved_by',
            'extension_approved_by_username',
            'extension_approval_status',
            'closure_comments',
            'closed_date',
            'closed_by',
            'closed_by_username',
            'department',
            'department_name',
            'assigned_to',
            'assigned_to_username',
            'coordinator',
            'coordinator_username',
            'is_recurring',
            'recurrence_count',
            'requires_management_review',
            'approvals',
            'documents',
            'comments',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'capa_id',
            'risk_priority_number',
            'phase_entered_at',
            'department_name',
            'assigned_to_username',
            'responsible_person_username',
            'coordinator_username',
            'closed_by_username',
            'root_cause_verified_by_username',
            'implementation_verified_by_username',
            'effectiveness_verified_by_username',
            'extension_approved_by_username',
            'approvals',
            'documents',
            'comments',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
    
    def get_risk_priority_number(self, obj):
        """Calculate and return risk priority number."""
        return obj.risk_priority_number
    
    def get_approvals(self, obj):
        """Return nested approvals."""
        approvals = obj.approvals.all()
        return CAPAApprovalSerializer(approvals, many=True).data
    
    def get_documents(self, obj):
        """Return nested documents."""
        documents = obj.documents.all()
        return CAPADocumentSerializer(documents, many=True).data
    
    def get_comments(self, obj):
        """Return root-level comments with nested replies."""
        root_comments = obj.comments.filter(parent__isnull=True)
        return CAPACommentSerializer(root_comments, many=True).data


class CAPACreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new CAPAs."""
    
    class Meta:
        model = CAPA
        fields = [
            'title',
            'description',
            'source',
            'source_reference',
            'complaint',
            'audit_finding',
            'deviation',
            'category',
            'priority',
            'capa_type',
            'department',
            'assigned_to',
            'coordinator',
            'requires_management_review',
        ]


# ============================================================================
# APPROVAL SERIALIZERS
# ============================================================================

class CAPAApprovalSerializer(serializers.ModelSerializer):
    """Serializer for CAPA approvals."""
    
    approver_username = serializers.CharField(
        source='approver.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = CAPAApproval
        fields = [
            'id',
            'capa',
            'phase',
            'approver',
            'approver_username',
            'approval_tier',
            'sequence',
            'status',
            'comments',
            'responded_at',
            'signature',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = [
            'id',
            'approver_username',
            'responded_at',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]


class ApprovalResponseSerializer(serializers.Serializer):
    """Serializer for approval responses."""

    status = serializers.ChoiceField(
        choices=['approved', 'rejected', 'deferred'],
        required=True
    )
    comments = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
    approval_id = serializers.IntegerField(required=True)


# ============================================================================
# DOCUMENT SERIALIZERS
# ============================================================================

class CAPADocumentSerializer(serializers.ModelSerializer):
    """Serializer for CAPA documents."""
    
    uploaded_by_username = serializers.CharField(
        source='uploaded_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = CAPADocument
        fields = [
            'id',
            'capa',
            'phase',
            'document_type',
            'title',
            'file',
            'file_hash',
            'description',
            'uploaded_by',
            'uploaded_by_username',
            'uploaded_at',
        ]
        read_only_fields = [
            'id',
            'file_hash',
            'uploaded_by_username',
            'uploaded_at',
        ]


# ============================================================================
# COMMENT SERIALIZERS
# ============================================================================

class CAPACommentReplySerializer(serializers.ModelSerializer):
    """Serializer for comment replies."""
    
    author_username = serializers.CharField(
        source='author.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = CAPAComment
        fields = [
            'id',
            'capa',
            'author',
            'author_username',
            'comment',
            'phase',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author_username',
            'created_at',
            'updated_at',
        ]


class CAPACommentSerializer(serializers.ModelSerializer):
    """Serializer for CAPA comments with nested replies."""
    
    author_username = serializers.CharField(
        source='author.username',
        read_only=True,
        allow_null=True
    )
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = CAPAComment
        fields = [
            'id',
            'capa',
            'author',
            'author_username',
            'comment',
            'phase',
            'parent',
            'replies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author_username',
            'replies',
            'created_at',
            'updated_at',
        ]
    
    def get_replies(self, obj):
        """Return nested replies."""
        replies = obj.replies.all()
        return CAPACommentReplySerializer(replies, many=True).data


# ============================================================================
# PHASE TRANSITION SERIALIZER
# ============================================================================

class PhaseTransitionSerializer(serializers.Serializer):
    """Serializer for phase transitions."""

    new_phase = serializers.ChoiceField(
        choices=[
            'investigation',
            'root_cause',
            'risk_affirmation',
            'capa_plan',
            'implementation',
            'effectiveness',
            'closure',
        ],
        required=True
    )
    comments = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )


# ============================================================================
# RISK MATRIX SERIALIZER
# ============================================================================

class RiskMatrixSerializer(serializers.Serializer):
    """Serializer for risk matrix calculations."""
    
    risk_severity = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        help_text="Severity: 1 (low) to 5 (high)"
    )
    risk_occurrence = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        help_text="Occurrence: 1 (low) to 5 (high)"
    )
    risk_detection = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        help_text="Detection: 1 (low) to 5 (high)"
    )


# ============================================================================
# EXTENSION REQUEST SERIALIZER
# ============================================================================

class ExtensionRequestSerializer(serializers.Serializer):
    """Serializer for extension requests."""
    
    extension_reason = serializers.CharField(
        max_length=1000,
        required=True
    )
    extension_new_due_date = serializers.DateField(
        required=True,
        help_text="New target completion date"
    )


# ============================================================================
# 5W ANALYSIS SERIALIZER
# ============================================================================

class FiveWAnalysisSerializer(serializers.Serializer):
    """Serializer for 5W analysis data."""
    
    what_happened = serializers.CharField(
        max_length=1000,
        required=True
    )
    when_happened = serializers.DateTimeField(
        required=False,
        allow_null=True
    )
    where_happened = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    who_affected = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    why_happened = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
    how_discovered = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True
    )
