from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    DesignProject,
    UserNeed,
    DesignInput,
    DesignOutput,
    VVProtocol,
    DesignReview,
    DesignTransfer,
    TraceabilityLink,
)

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DesignProjectListSerializer(serializers.ModelSerializer):
    project_lead = UserBriefSerializer(read_only=True)
    project_lead_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='project_lead'
    )

    class Meta:
        model = DesignProject
        fields = [
            'id', 'project_id', 'title', 'product_type', 'current_phase',
            'status', 'project_lead', 'project_lead_id', 'regulatory_pathway',
            'target_completion_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['project_id', 'created_at', 'updated_at']


class DesignProjectDetailSerializer(serializers.ModelSerializer):
    project_lead = UserBriefSerializer(read_only=True)
    project_lead_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='project_lead'
    )
    user_needs_count = serializers.SerializerMethodField()
    design_inputs_count = serializers.SerializerMethodField()
    design_outputs_count = serializers.SerializerMethodField()
    vv_protocols_count = serializers.SerializerMethodField()

    class Meta:
        model = DesignProject
        fields = [
            'id', 'project_id', 'title', 'description', 'product_type',
            'current_phase', 'status', 'project_lead', 'project_lead_id',
            'regulatory_pathway', 'target_completion_date', 'department',
            'product_line', 'user_needs_count', 'design_inputs_count',
            'design_outputs_count', 'vv_protocols_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['project_id', 'created_at', 'updated_at']

    def get_user_needs_count(self, obj):
        return obj.user_needs.count()

    def get_design_inputs_count(self, obj):
        return obj.design_inputs.count()

    def get_design_outputs_count(self, obj):
        return obj.design_outputs.count()

    def get_vv_protocols_count(self, obj):
        return obj.vv_protocols.count()


class UserNeedListSerializer(serializers.ModelSerializer):
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )

    class Meta:
        model = UserNeed
        fields = [
            'id', 'need_id', 'project', 'description', 'source', 'priority',
            'status', 'approved_by', 'approved_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['need_id', 'created_at', 'updated_at']


class UserNeedDetailSerializer(serializers.ModelSerializer):
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )

    class Meta:
        model = UserNeed
        fields = [
            'id', 'need_id', 'project', 'description', 'source', 'priority',
            'acceptance_criteria', 'rationale', 'status', 'approved_by',
            'approved_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['need_id', 'created_at', 'updated_at']


class DesignInputListSerializer(serializers.ModelSerializer):
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )

    class Meta:
        model = DesignInput
        fields = [
            'id', 'input_id', 'project', 'specification', 'input_type',
            'status', 'approved_by', 'approved_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['input_id', 'created_at', 'updated_at']


class DesignInputDetailSerializer(serializers.ModelSerializer):
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )
    linked_user_needs = serializers.PrimaryKeyRelatedField(
        queryset=UserNeed.objects.all(), many=True, required=False
    )

    class Meta:
        model = DesignInput
        fields = [
            'id', 'input_id', 'project', 'specification', 'measurable_criteria',
            'input_type', 'tolerance', 'test_method', 'linked_user_needs',
            'status', 'approved_by', 'approved_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['input_id', 'created_at', 'updated_at']


class DesignOutputListSerializer(serializers.ModelSerializer):
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )

    class Meta:
        model = DesignOutput
        fields = [
            'id', 'output_id', 'project', 'description', 'output_type',
            'revision', 'status', 'approved_by', 'approved_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['output_id', 'created_at', 'updated_at']


class DesignOutputDetailSerializer(serializers.ModelSerializer):
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )
    linked_inputs = serializers.PrimaryKeyRelatedField(
        queryset=DesignInput.objects.all(), many=True, required=False
    )

    class Meta:
        model = DesignOutput
        fields = [
            'id', 'output_id', 'project', 'description', 'output_type', 'file',
            'revision', 'linked_inputs', 'status', 'approved_by', 'approved_by_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['output_id', 'created_at', 'updated_at']


class VVProtocolListSerializer(serializers.ModelSerializer):
    executed_by = UserBriefSerializer(read_only=True)
    executed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='executed_by', required=False
    )
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )

    class Meta:
        model = VVProtocol
        fields = [
            'id', 'protocol_id', 'project', 'title', 'protocol_type', 'status',
            'result', 'execution_date', 'executed_by', 'executed_by_id',
            'approved_by', 'approved_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['protocol_id', 'created_at', 'updated_at']


class VVProtocolDetailSerializer(serializers.ModelSerializer):
    executed_by = UserBriefSerializer(read_only=True)
    executed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='executed_by', required=False
    )
    approved_by = UserBriefSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='approved_by', required=False
    )
    linked_inputs = serializers.PrimaryKeyRelatedField(
        queryset=DesignInput.objects.all(), many=True, required=False
    )
    linked_outputs = serializers.PrimaryKeyRelatedField(
        queryset=DesignOutput.objects.all(), many=True, required=False
    )

    class Meta:
        model = VVProtocol
        fields = [
            'id', 'protocol_id', 'project', 'title', 'protocol_type', 'test_method',
            'acceptance_criteria', 'sample_size', 'linked_inputs', 'linked_outputs',
            'status', 'execution_date', 'result', 'result_summary', 'deviations_noted',
            'executed_by', 'executed_by_id', 'approved_by', 'approved_by_id',
            'file', 'result_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['protocol_id', 'created_at', 'updated_at']


class DesignReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignReview
        fields = [
            'id', 'review_id', 'project', 'phase', 'review_date', 'status',
            'outcome', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']


class DesignReviewDetailSerializer(serializers.ModelSerializer):
    attendees = UserBriefSerializer(read_only=True, many=True)
    attendees_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='attendees', many=True, required=False
    )

    class Meta:
        model = DesignReview
        fields = [
            'id', 'review_id', 'project', 'phase', 'review_date', 'attendees',
            'attendees_ids', 'agenda', 'minutes', 'action_items', 'outcome',
            'conditions', 'follow_up_date', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']


class DesignTransferListSerializer(serializers.ModelSerializer):
    confirmed_by = UserBriefSerializer(read_only=True)
    confirmed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='confirmed_by', required=False
    )

    class Meta:
        model = DesignTransfer
        fields = [
            'id', 'transfer_id', 'project', 'status', 'manufacturing_site',
            'production_readiness_confirmed', 'confirmed_by', 'confirmed_by_id',
            'confirmed_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['transfer_id', 'created_at', 'updated_at']


class DesignTransferDetailSerializer(serializers.ModelSerializer):
    confirmed_by = UserBriefSerializer(read_only=True)
    confirmed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='confirmed_by', required=False
    )

    class Meta:
        model = DesignTransfer
        fields = [
            'id', 'transfer_id', 'project', 'description', 'transfer_checklist',
            'manufacturing_site', 'production_readiness_confirmed', 'confirmed_by',
            'confirmed_by_id', 'confirmed_date', 'linked_document', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['transfer_id', 'created_at', 'updated_at']


class TraceabilityLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TraceabilityLink
        fields = [
            'id', 'project', 'user_need', 'design_input', 'design_output',
            'vv_protocol', 'link_status', 'gap_description', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
