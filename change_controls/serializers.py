from rest_framework import serializers
from .models import (
    ChangeControl,
    ChangeControlApproval,
    ChangeControlTask,
    ChangeControlAttachment,
    ChangeControlComment,
)


class ChangeControlCommentSerializer(serializers.ModelSerializer):
    """Serializer for change control comments with threading support."""
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies_list = serializers.SerializerMethodField()

    class Meta:
        model = ChangeControlComment
        fields = [
            'id',
            'change_control',
            'author',
            'author_username',
            'comment',
            'parent',
            'created_at',
            'replies_list',
        ]
        read_only_fields = ['id', 'created_at', 'author_username']

    def get_replies_list(self, obj):
        """Get nested reply comments."""
        child_replies = obj.replies.all()
        return ChangeControlCommentSerializer(child_replies, many=True, read_only=True).data


class ChangeControlAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for change control attachments."""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ChangeControlAttachment
        fields = [
            'id',
            'change_control',
            'file_name',
            'file',
            'file_url',
            'description',
            'uploaded_by',
            'uploaded_by_username',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_username']

    def get_file_url(self, obj):
        """Get absolute file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ChangeControlTaskSerializer(serializers.ModelSerializer):
    """Serializer for change control tasks."""
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = ChangeControlTask
        fields = [
            'id',
            'change_control',
            'title',
            'description',
            'assigned_to',
            'assigned_to_username',
            'due_date',
            'status',
            'sequence',
            'completed_date',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'assigned_to_username']


class ChangeControlApprovalSerializer(serializers.ModelSerializer):
    """Serializer for change control approvals."""
    approver_username = serializers.CharField(source='approver.username', read_only=True)

    class Meta:
        model = ChangeControlApproval
        fields = [
            'id',
            'change_control',
            'approver',
            'approver_username',
            'approval_role',
            'sequence',
            'status',
            'comments',
            'responded_at',
            'signature',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approver_username']


class ApprovalResponseSerializer(serializers.Serializer):
    """Serializer for change control approval responses."""
    status = serializers.ChoiceField(
        choices=['approved', 'rejected', 'deferred'],
        help_text='The approval status'
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Additional comments for the approval'
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Password for e-signature authentication'
    )


class StageTransitionSerializer(serializers.Serializer):
    """Serializer for change control stage transitions."""
    target_stage = serializers.ChoiceField(
        choices=[s[0] for s in ChangeControl.STAGE_CHOICES],
        help_text='The target stage to transition to'
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Comments about the transition'
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Password for e-signature authentication'
    )


class ChangeControlCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating change controls."""

    class Meta:
        model = ChangeControl
        fields = [
            'id',
            'change_control_id',
            'title',
            'description',
            'change_type',
            'change_category',
            'risk_level',
            'current_stage',
            'department',
            'justification',
            'impact_summary',
            'proposed_implementation_date',
            'submitted_date',
            'affected_areas',
            'affected_documents',
            'affected_processes',
            'affected_products',
            'is_emergency',
            'created_at',
        ]
        read_only_fields = ['id', 'change_control_id', 'created_at', 'submitted_date']


class ChangeControlListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing change controls."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    proposed_by_username = serializers.CharField(source='proposed_by.username', read_only=True)

    class Meta:
        model = ChangeControl
        fields = [
            'id',
            'change_control_id',
            'title',
            'change_type',
            'change_category',
            'risk_level',
            'current_stage',
            'department_name',
            'proposed_by_username',
            'submitted_date',
            'is_emergency',
        ]
        read_only_fields = fields


class ChangeControlDetailSerializer(serializers.ModelSerializer):
    """Full serializer for change control details."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    proposed_by_username = serializers.CharField(source='proposed_by.username', read_only=True)
    approvals = ChangeControlApprovalSerializer(many=True, read_only=True)
    tasks = ChangeControlTaskSerializer(many=True, read_only=True)
    attachments = ChangeControlAttachmentSerializer(many=True, read_only=True)
    comments = ChangeControlCommentSerializer(many=True, read_only=True)

    class Meta:
        model = ChangeControl
        fields = [
            'id',
            'change_control_id',
            'title',
            'description',
            'change_type',
            'change_category',
            'risk_level',
            'current_stage',
            'stage_entered_at',
            # Scope
            'affected_areas',
            'affected_documents',
            'affected_processes',
            'affected_products',
            # Impact
            'impact_summary',
            'quality_impact',
            'regulatory_impact',
            'safety_impact',
            'training_impact',
            'validation_impact',
            'documentation_impact',
            # Planning
            'department',
            'department_name',
            'proposed_by',
            'proposed_by_username',
            'justification',
            'proposed_implementation_date',
            'actual_implementation_date',
            'rollback_plan',
            # Verification
            'verification_method',
            'verification_results',
            'verification_completed',
            'verified_by',
            'verified_at',
            # Assignment
            'assigned_to',
            'sponsor',
            # Linked records
            'related_capa',
            'related_deviation',
            # Dates
            'submitted_date',
            'target_completion_date',
            'actual_completion_date',
            'closed_date',
            'closed_by',
            # Flags
            'requires_validation',
            'requires_regulatory_notification',
            'is_emergency',
            # Related objects
            'approvals',
            'tasks',
            'attachments',
            'comments',
            # Audit
            'created_by',
            'created_at',
            'updated_by',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'change_control_id', 'created_at', 'updated_at',
            'department_name', 'proposed_by_username',
        ]
