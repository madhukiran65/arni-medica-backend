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
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ChangeControlComment
        fields = [
            'id',
            'change_control',
            'author',
            'author_username',
            'comment_text',
            'parent_comment',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author_username']

    def get_replies(self, obj):
        """Get nested reply comments."""
        replies = obj.changecontrolcomment_set.all()
        return ChangeControlCommentSerializer(replies, many=True, read_only=True).data


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
            'file_type',
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
            'task_description',
            'assigned_to',
            'assigned_to_username',
            'due_date',
            'status',
            'priority',
            'completion_date',
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
            'approval_stage',
            'approval_status',
            'comments',
            'approval_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approver_username']


class ApprovalResponseSerializer(serializers.Serializer):
    """Serializer for change control approval responses."""
    status = serializers.ChoiceField(
        choices=['approved', 'rejected', 'pending'],
        help_text='The approval status'
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Additional comments for the approval'
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Password for authentication'
    )


class StageTransitionSerializer(serializers.Serializer):
    """Serializer for change control stage transitions."""
    target_stage = serializers.CharField(help_text='The target stage to transition to')
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Comments about the transition'
    )
    password = serializers.CharField(
        write_only=True,
        help_text='Password for authentication'
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
            'expected_impact',
            'implementation_date',
            'submitted_date',
            'created_at',
        ]
        read_only_fields = ['id', 'change_control_id', 'created_at', 'submitted_date']


class ChangeControlListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing change controls."""
    department_name = serializers.CharField(source='department.name', read_only=True)

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
            'submitted_date',
        ]
        read_only_fields = ['id', 'change_control_id', 'department_name', 'submitted_date']


class ChangeControlDetailSerializer(serializers.ModelSerializer):
    """Full serializer for change control details."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    approvals = ChangeControlApprovalSerializer(
        source='changecontrolapproval_set',
        many=True,
        read_only=True
    )
    tasks = ChangeControlTaskSerializer(
        source='changecontroltask_set',
        many=True,
        read_only=True
    )
    attachments = ChangeControlAttachmentSerializer(
        source='changecontrolattachment_set',
        many=True,
        read_only=True
    )
    comments = ChangeControlCommentSerializer(
        source='changecontrolcomment_set',
        many=True,
        read_only=True
    )
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True)

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
            'department_name',
            'justification',
            'expected_impact',
            'implementation_date',
            'submitted_by',
            'submitted_by_username',
            'submitted_date',
            'approvals',
            'tasks',
            'attachments',
            'comments',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'change_control_id',
            'created_at',
            'updated_at',
            'department_name',
            'submitted_by_username',
        ]
