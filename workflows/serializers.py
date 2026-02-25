"""
Workflow Engine REST API Serializers.
"""
from rest_framework import serializers
from .models import (
    WorkflowDefinition, WorkflowStage, WorkflowTransition,
    WorkflowRecord, WorkflowHistory, WorkflowApprovalGate,
    WorkflowApprovalRequest, WorkflowDelegation,
)


class WorkflowStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStage
        fields = [
            'id', 'name', 'slug', 'sequence', 'description',
            'color', 'icon', 'required_fields', 'requires_approval',
            'required_approvers_count', 'requires_signature',
            'is_initial', 'is_terminal', 'allows_edit',
            'auto_advance', 'sla_days',
        ]


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    from_stage_name = serializers.CharField(source='from_stage.name', read_only=True)
    to_stage_name = serializers.CharField(source='to_stage.name', read_only=True)

    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'from_stage', 'from_stage_name', 'to_stage', 'to_stage_name',
            'label', 'description', 'button_color', 'required_permission',
            'required_roles', 'requires_comment', 'is_rejection',
            'estimated_duration_days',
        ]


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    stages = WorkflowStageSerializer(many=True, read_only=True)
    transitions = WorkflowTransitionSerializer(many=True, read_only=True)
    stage_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = [
            'id', 'name', 'description', 'model_type', 'is_active',
            'stage_count', 'stages', 'transitions',
            'created_at', 'updated_at',
        ]


class WorkflowDefinitionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    stage_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkflowDefinition
        fields = ['id', 'name', 'description', 'model_type', 'is_active', 'stage_count']


class WorkflowApprovalGateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowApprovalGate
        fields = [
            'id', 'name', 'required_role', 'required_count',
            'approval_mode', 'sequence', 'estimated_response_days',
        ]


class WorkflowApprovalRequestSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(
        source='approver.get_full_name', read_only=True
    )
    gate_name = serializers.CharField(source='gate.name', read_only=True)
    stage_name = serializers.CharField(source='gate.stage.name', read_only=True)
    workflow_name = serializers.CharField(
        source='workflow_record.workflow.name', read_only=True
    )

    class Meta:
        model = WorkflowApprovalRequest
        fields = [
            'id', 'gate', 'gate_name', 'stage_name', 'workflow_name',
            'approver', 'approver_name', 'status',
            'responded_at', 'comments', 'requested_at', 'due_date',
        ]


class WorkflowHistorySerializer(serializers.ModelSerializer):
    from_stage_name = serializers.CharField(source='from_stage.name', read_only=True)
    to_stage_name = serializers.CharField(source='to_stage.name', read_only=True)
    transitioned_by_name = serializers.CharField(
        source='transitioned_by.get_full_name', read_only=True
    )
    has_signature = serializers.BooleanField(
        source='signature', read_only=True
    )

    class Meta:
        model = WorkflowHistory
        fields = [
            'id', 'from_stage_name', 'to_stage_name',
            'transitioned_by', 'transitioned_by_name',
            'transitioned_at', 'comments',
            'time_in_stage_seconds', 'has_signature',
        ]


class WorkflowRecordSerializer(serializers.ModelSerializer):
    current_stage_name = serializers.CharField(
        source='current_stage.name', read_only=True
    )
    current_stage_slug = serializers.CharField(
        source='current_stage.slug', read_only=True
    )
    current_stage_color = serializers.CharField(
        source='current_stage.color', read_only=True
    )
    workflow_name = serializers.CharField(
        source='workflow.name', read_only=True
    )
    allows_edit = serializers.BooleanField(
        source='current_stage.allows_edit', read_only=True
    )

    class Meta:
        model = WorkflowRecord
        fields = [
            'id', 'workflow', 'workflow_name',
            'current_stage', 'current_stage_name', 'current_stage_slug',
            'current_stage_color', 'allows_edit',
            'entered_stage_at', 'estimated_exit_date',
            'stage_entry_count', 'is_active', 'is_overdue',
            'created_at',
        ]


class WorkflowRecordDetailSerializer(WorkflowRecordSerializer):
    """Detailed view with history and approval status."""
    history = WorkflowHistorySerializer(many=True, read_only=True)
    approval_requests = WorkflowApprovalRequestSerializer(many=True, read_only=True)
    valid_transitions = serializers.SerializerMethodField()
    approval_status = serializers.SerializerMethodField()

    class Meta(WorkflowRecordSerializer.Meta):
        fields = WorkflowRecordSerializer.Meta.fields + [
            'history', 'approval_requests',
            'valid_transitions', 'approval_status',
        ]

    def get_valid_transitions(self, obj):
        from .services import WorkflowService
        return WorkflowService.get_valid_transitions(obj)

    def get_approval_status(self, obj):
        from .services import WorkflowService
        return WorkflowService.get_approval_status(obj)


# === Action Serializers (for POST endpoints) ===

class TransitionActionSerializer(serializers.Serializer):
    """Input for workflow transition."""
    to_stage_slug = serializers.SlugField(required=True)
    comments = serializers.CharField(required=False, default='', allow_blank=True)
    signature_password = serializers.CharField(
        required=False, default=None, allow_null=True,
        help_text="Password for electronic signature (required for signature-gated stages)"
    )


class ApprovalResponseSerializer(serializers.Serializer):
    """Input for approval response."""
    status = serializers.ChoiceField(choices=['approved', 'rejected', 'deferred'])
    comments = serializers.CharField(required=False, default='', allow_blank=True)
    signature_password = serializers.CharField(
        required=False, default=None, allow_null=True,
    )


class AddApproverSerializer(serializers.Serializer):
    """Input for adding an approver to a gate."""
    gate_id = serializers.IntegerField()
    approver_id = serializers.IntegerField()


class ExtendDeadlineSerializer(serializers.Serializer):
    """Input for extending workflow deadline."""
    days = serializers.IntegerField(min_value=1, max_value=365)
    reason = serializers.CharField()


class WorkflowDelegationSerializer(serializers.ModelSerializer):
    delegator_name = serializers.CharField(
        source='delegator.get_full_name', read_only=True
    )
    delegate_name = serializers.CharField(
        source='delegate.get_full_name', read_only=True
    )

    class Meta:
        model = WorkflowDelegation
        fields = [
            'id', 'delegator', 'delegator_name',
            'delegate', 'delegate_name',
            'workflow', 'start_date', 'end_date',
            'reason', 'is_active', 'created_at',
        ]
