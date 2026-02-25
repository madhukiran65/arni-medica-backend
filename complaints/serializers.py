from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    Complaint,
    ComplaintAttachment,
    ComplaintComment,
    MIRRecord,
)


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
# COMPLAINT ATTACHMENT SERIALIZER
# ============================================================================
class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    """Complaint file attachment"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    attachment_type_display = serializers.CharField(source='get_attachment_type_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintAttachment
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size', 'file_size_mb',
            'attachment_type', 'attachment_type_display', 'description',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_at']

    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2)


# ============================================================================
# COMPLAINT COMMENT SERIALIZER
# ============================================================================
class ComplaintCommentSerializer(serializers.ModelSerializer):
    """Complaint comment with threaded replies"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintComment
        fields = [
            'id', 'complaint', 'author', 'author_name', 'author_username',
            'comment', 'parent', 'created_at', 'replies'
        ]
        read_only_fields = ['id', 'created_at']

    def get_replies(self, obj):
        if obj.parent_id is None:
            replies = obj.replies.all()
            return ComplaintCommentSerializer(replies, many=True).data
        return []


# ============================================================================
# MIR RECORD SERIALIZER
# ============================================================================
class MIRRecordSerializer(serializers.ModelSerializer):
    """Medical Incident Report (MIR) record"""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    parent_mir_number = serializers.CharField(source='parent_mir.mir_number', read_only=True, allow_null=True)

    class Meta:
        model = MIRRecord
        fields = [
            'id', 'complaint', 'mir_number', 'report_type', 'report_type_display',
            'parent_mir', 'parent_mir_number', 'submitted_date', 'submitted_to',
            'narrative', 'patient_outcome', 'device_evaluation_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# COMPLAINT LIST SERIALIZER
# ============================================================================
class ComplaintListSerializer(serializers.ModelSerializer):
    """Compact complaint list view"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    days_open = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            'id', 'complaint_id', 'title', 'status', 'status_display',
            'severity', 'severity_display', 'priority', 'priority_display',
            'event_type', 'event_type_display', 'is_reportable_to_fda',
            'received_date', 'days_open', 'department', 'department_name',
            'assigned_to', 'assigned_to_name', 'assigned_to_username'
        ]
        read_only_fields = ['id']

    def get_days_open(self, obj):
        end_date = obj.actual_closure_date if obj.actual_closure_date else timezone.now().date()
        received_date = obj.received_date.date() if hasattr(obj.received_date, 'date') else obj.received_date
        delta = end_date - received_date
        return delta.days


# ============================================================================
# COMPLAINT DETAIL SERIALIZER
# ============================================================================
class ComplaintDetailSerializer(serializers.ModelSerializer):
    """Full complaint details with attachments and comments"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    complainant_type_display = serializers.CharField(source='get_complainant_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    patient_sex_display = serializers.CharField(source='get_patient_sex_display', read_only=True, allow_null=True)
    device_usage_display = serializers.CharField(source='get_device_usage_display', read_only=True, allow_null=True)
    device_available_display = serializers.CharField(source='get_device_available_display', read_only=True, allow_null=True)
    mdr_submission_status_display = serializers.CharField(source='get_mdr_submission_status_display', read_only=True)
    mdr_report_type_display = serializers.CharField(source='get_mdr_report_type_display', read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True, allow_null=True)
    investigated_by_name = serializers.CharField(source='investigated_by.get_full_name', read_only=True, allow_null=True)
    reportability_determined_by_name = serializers.CharField(source='reportability_determined_by.get_full_name', read_only=True, allow_null=True)
    closed_by_name = serializers.CharField(source='closed_by.get_full_name', read_only=True, allow_null=True)
    attachments = ComplaintAttachmentSerializer(many=True, read_only=True)
    mir_records = MIRRecordSerializer(many=True, read_only=True)
    root_comments = serializers.SerializerMethodField()
    days_open = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            'id', 'complaint_id', 'title', 'description', 'status', 'status_display',
            'stage_entered_at', 'complainant_name', 'complainant_email', 'complainant_phone',
            'complainant_organization', 'complainant_type', 'complainant_type_display',
            'product_name', 'product_code', 'product_lot_number', 'product_serial_number',
            'manufacture_date', 'expiry_date', 'product_description', 'event_date',
            'event_description', 'event_location', 'event_country', 'sample_available',
            'sample_received_date', 'category', 'category_display', 'severity',
            'severity_display', 'priority', 'priority_display', 'event_type',
            'event_type_display', 'patient_age', 'patient_sex', 'patient_sex_display',
            'patient_weight_kg', 'health_effect', 'device_usage', 'device_usage_display',
            'device_available', 'device_available_display', 'is_reportable_to_fda',
            'reportability_determination_date', 'reportability_justification',
            'reportability_determined_by', 'reportability_determined_by_name',
            'awareness_date', 'mdr_report_number', 'mdr_submission_date',
            'mdr_submission_status', 'mdr_submission_status_display', 'mdr_report_type',
            'mdr_report_type_display', 'fda_reference_number', 'investigation_summary',
            'root_cause', 'investigation_completed_date', 'investigated_by',
            'investigated_by_name', 'resolution_description', 'capa', 'corrective_action',
            'preventive_action', 'department', 'department_name', 'assigned_to',
            'assigned_to_name', 'assigned_to_username', 'coordinator', 'coordinator_name',
            'received_date', 'target_closure_date', 'actual_closure_date', 'closed_by',
            'closed_by_name', 'is_trending', 'trend_category', 'requires_field_action',
            'attachments', 'mir_records', 'root_comments', 'days_open',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_root_comments(self, obj):
        root_comments = obj.comments.filter(parent__isnull=True)
        return ComplaintCommentSerializer(root_comments, many=True).data

    def get_days_open(self, obj):
        end_date = obj.actual_closure_date if obj.actual_closure_date else timezone.now().date()
        received_date = obj.received_date.date() if hasattr(obj.received_date, 'date') else obj.received_date
        delta = end_date - received_date
        return delta.days


# ============================================================================
# COMPLAINT CREATE SERIALIZER
# ============================================================================
class ComplaintCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new complaints"""

    class Meta:
        model = Complaint
        fields = [
            'title', 'description', 'complainant_name', 'complainant_email',
            'complainant_phone', 'complainant_organization', 'complainant_type',
            'product_name', 'product_code', 'product_lot_number', 'product_serial_number',
            'manufacture_date', 'expiry_date', 'product_description', 'event_date',
            'event_description', 'event_location', 'event_country', 'sample_available',
            'sample_received_date', 'category', 'severity', 'priority', 'event_type',
            'patient_age', 'patient_sex', 'patient_weight_kg', 'health_effect',
            'device_usage', 'device_available', 'department'
        ]
        read_only_fields = []

    def validate(self, data):
        """Validate required fields"""
        if not data.get('event_description'):
            raise serializers.ValidationError("Event description is required")
        if not data.get('category'):
            raise serializers.ValidationError("Category is required")
        return data


# ============================================================================
# REPORTABILITY DETERMINATION SERIALIZER
# ============================================================================
class ReportabilityDeterminationSerializer(serializers.Serializer):
    """Action serializer for determining reportability to FDA"""
    is_reportable_to_fda = serializers.BooleanField()
    reportability_justification = serializers.CharField(
        max_length=5000,
        help_text="Explanation of reportability determination"
    )


# ============================================================================
# MDR SUBMISSION SERIALIZER
# ============================================================================
class MDRSubmissionSerializer(serializers.Serializer):
    """Action serializer for MDR submission"""
    mdr_report_number = serializers.CharField(
        max_length=100,
        help_text="FDA assigned MDR report number"
    )
    mdr_submission_date = serializers.DateField()
    mdr_report_type = serializers.ChoiceField(
        choices=Complaint.MDR_REPORT_TYPE_CHOICES,
        help_text="Type of MDR report"
    )
