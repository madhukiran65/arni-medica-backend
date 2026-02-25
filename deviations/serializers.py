from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Deviation, DeviationAttachment, DeviationComment


# ============================================================================
# USER SERIALIZER
# ============================================================================
class UserSerializer(serializers.ModelSerializer):
    """Basic user information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']


# ============================================================================
# DEVIATION ATTACHMENT SERIALIZER
# ============================================================================
class DeviationAttachmentSerializer(serializers.ModelSerializer):
    """Deviation file attachment"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = DeviationAttachment
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size', 'file_size_mb',
            'description', 'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_at']

    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2)


# ============================================================================
# DEVIATION COMMENT SERIALIZER
# ============================================================================
class DeviationCommentSerializer(serializers.ModelSerializer):
    """Deviation comment with threaded replies"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True, allow_null=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = DeviationComment
        fields = [
            'id', 'deviation', 'author', 'author_name', 'author_username',
            'comment', 'stage', 'stage_display', 'parent', 'created_at', 'replies'
        ]
        read_only_fields = ['id', 'created_at']

    def get_replies(self, obj):
        if obj.parent_id is None:
            replies = obj.replies.all()
            return DeviationCommentSerializer(replies, many=True).data
        return []


# ============================================================================
# DEVIATION LIST SERIALIZER
# ============================================================================
class DeviationListSerializer(serializers.ModelSerializer):
    """Compact deviation list view"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    current_stage_display = serializers.CharField(source='get_current_stage_display', read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)

    class Meta:
        model = Deviation
        fields = [
            'id', 'deviation_id', 'title', 'severity', 'severity_display',
            'current_stage', 'current_stage_display', 'department', 'department_name',
            'assigned_to', 'assigned_to_username', 'assigned_to_name', 'reported_by_name',
            'reported_date', 'days_open', 'requires_capa', 'regulatory_reportable'
        ]
        read_only_fields = ['id']


# ============================================================================
# DEVIATION DETAIL SERIALIZER
# ============================================================================
class DeviationDetailSerializer(serializers.ModelSerializer):
    """Full deviation details with attachments and comments"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    investigated_by_name = serializers.CharField(source='investigated_by.get_full_name', read_only=True, allow_null=True)
    qa_reviewer_name = serializers.CharField(source='qa_reviewer.get_full_name', read_only=True, allow_null=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    deviation_type_display = serializers.CharField(source='get_deviation_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    current_stage_display = serializers.CharField(source='get_current_stage_display', read_only=True)
    disposition_display = serializers.CharField(source='get_disposition_display', read_only=True, allow_null=True)
    attachments = DeviationAttachmentSerializer(many=True, read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    root_comments = serializers.SerializerMethodField()

    class Meta:
        model = Deviation
        fields = [
            'id', 'deviation_id', 'title', 'description', 'deviation_type',
            'deviation_type_display', 'category', 'category_display', 'severity',
            'severity_display', 'source', 'source_display', 'source_reference',
            'process_affected', 'product_affected', 'batch_lot_number',
            'quantity_affected', 'impact_assessment', 'patient_safety_impact',
            'current_stage', 'current_stage_display', 'stage_entered_at',
            'root_cause', 'investigation_summary', 'investigated_by',
            'investigated_by_name', 'investigation_completed_at',
            'corrective_action', 'preventive_action', 'capa', 'disposition',
            'disposition_display', 'disposition_justification', 'reported_date',
            'target_closure_date', 'actual_closure_date', 'department',
            'department_name', 'reported_by', 'reported_by_name', 'assigned_to',
            'assigned_to_name', 'assigned_to_username', 'qa_reviewer',
            'qa_reviewer_name', 'requires_capa', 'is_recurring',
            'regulatory_reportable', 'attachments', 'root_comments', 'days_open',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_root_comments(self, obj):
        root_comments = obj.comments.filter(parent__isnull=True)
        return DeviationCommentSerializer(root_comments, many=True).data


# ============================================================================
# DEVIATION CREATE SERIALIZER
# ============================================================================
class DeviationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new deviations"""

    class Meta:
        model = Deviation
        fields = [
            'title', 'description', 'deviation_type', 'category', 'severity',
            'source', 'source_reference', 'process_affected', 'product_affected',
            'batch_lot_number', 'quantity_affected', 'impact_assessment',
            'patient_safety_impact', 'department', 'reported_by'
        ]
        read_only_fields = []

    def validate(self, data):
        """Validate required fields based on deviation type"""
        if not data.get('impact_assessment'):
            raise serializers.ValidationError("Impact assessment is required")
        return data


# ============================================================================
# STAGE TRANSITION SERIALIZER
# ============================================================================
class StageTransitionSerializer(serializers.Serializer):
    """Action serializer for transitioning deviation to next stage"""
    target_stage = serializers.ChoiceField(
        choices=Deviation.STAGE_CHOICES,
        help_text="Target stage to transition to"
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
        help_text="Comments for this stage transition"
    )
    password = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Current user password for verification"
    )

    def validate(self, data):
        """Validate stage transition"""
        target_stage = data.get('target_stage')
        current_instance = self.context.get('instance')
        
        if current_instance:
            current_stage = current_instance.current_stage
            valid_transitions = self._get_valid_transitions(current_stage)
            
            if target_stage not in valid_transitions:
                raise serializers.ValidationError(
                    f"Cannot transition from {current_stage} to {target_stage}"
                )
        
        return data

    def _get_valid_transitions(self, current_stage):
        """Define valid stage transitions"""
        transitions = {
            Deviation.STAGE_OPENED: [Deviation.STAGE_QA_REVIEW],
            Deviation.STAGE_QA_REVIEW: [Deviation.STAGE_INVESTIGATION, Deviation.STAGE_OPENED],
            Deviation.STAGE_INVESTIGATION: [Deviation.STAGE_CAPA_PLAN, Deviation.STAGE_QA_REVIEW],
            Deviation.STAGE_CAPA_PLAN: [Deviation.STAGE_PENDING_CAPA_APPROVAL, Deviation.STAGE_INVESTIGATION],
            Deviation.STAGE_PENDING_CAPA_APPROVAL: [Deviation.STAGE_PENDING_CAPA_COMPLETION, Deviation.STAGE_CAPA_PLAN],
            Deviation.STAGE_PENDING_CAPA_COMPLETION: [Deviation.STAGE_PENDING_FINAL_APPROVAL, Deviation.STAGE_PENDING_CAPA_APPROVAL],
            Deviation.STAGE_PENDING_FINAL_APPROVAL: [Deviation.STAGE_COMPLETED, Deviation.STAGE_PENDING_CAPA_COMPLETION],
            Deviation.STAGE_COMPLETED: [],
        }
        return transitions.get(current_stage, [])
