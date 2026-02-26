from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    Complaint,
    ComplaintAttachment,
    MIRRecord,
    ComplaintComment,
    PMSPlan,
    TrendAnalysis,
    PMSReport,
    VigilanceReport,
    LiteratureReview,
    SafetySignal,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ComplaintListSerializer(serializers.ModelSerializer):
    """List serializer for Complaint"""

    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True,
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
    )

    class Meta:
        model = Complaint
        fields = [
            'id',
            'complaint_id',
            'title',
            'status',
            'severity',
            'priority',
            'product_name',
            'event_type',
            'is_reportable_to_fda',
            'mdr_submission_status',
            'assigned_to',
            'assigned_to_name',
            'department',
            'department_name',
            'received_date',
            'created_at',
        ]
        read_only_fields = ['id', 'complaint_id', 'created_at']


class ComplaintDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for Complaint"""

    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False,
    )
    investigated_by = UserSerializer(read_only=True)
    investigated_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='investigated_by',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = [
            'id',
            'complaint_id',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]


class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ComplaintAttachment"""

    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = ComplaintAttachment
        fields = [
            'id',
            'complaint',
            'file',
            'file_name',
            'file_type',
            'file_size',
            'attachment_type',
            'description',
            'uploaded_by',
            'uploaded_by_name',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at']


class MIRRecordListSerializer(serializers.ModelSerializer):
    """List serializer for MIRRecord"""

    complaint_id = serializers.CharField(
        source='complaint.complaint_id',
        read_only=True,
    )

    class Meta:
        model = MIRRecord
        fields = [
            'id',
            'complaint',
            'complaint_id',
            'mir_number',
            'report_type',
            'submitted_date',
            'created_at',
        ]
        read_only_fields = ['id', 'mir_number', 'created_at']


class MIRRecordDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for MIRRecord"""

    class Meta:
        model = MIRRecord
        fields = '__all__'
        read_only_fields = ['id', 'mir_number', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ComplaintCommentSerializer(serializers.ModelSerializer):
    """Serializer for ComplaintComment"""

    author_name = serializers.CharField(
        source='author.get_full_name',
        read_only=True,
    )

    class Meta:
        model = ComplaintComment
        fields = [
            'id',
            'complaint',
            'author',
            'author_name',
            'comment',
            'parent',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


# ============================================================================
# PMS (Post-Market Surveillance) Serializers - Merged from pms app
# ============================================================================


class PMSPlanListSerializer(serializers.ModelSerializer):
    """List serializer for PMSPlan"""

    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True,
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
    )

    class Meta:
        model = PMSPlan
        fields = [
            'id',
            'plan_id',
            'title',
            'product_name',
            'product_line',
            'product_line_name',
            'plan_version',
            'review_frequency',
            'status',
            'effective_date',
            'next_review_date',
            'responsible_person',
            'responsible_person_name',
            'department',
            'department_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'plan_id', 'created_at', 'updated_at']


class PMSPlanDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for PMSPlan"""

    responsible_person = UserSerializer(read_only=True)
    responsible_person_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='responsible_person',
        write_only=True,
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
    )

    class Meta:
        model = PMSPlan
        fields = [
            'id',
            'plan_id',
            'title',
            'product_name',
            'product_line',
            'product_line_name',
            'plan_version',
            'data_sources',
            'monitoring_criteria',
            'review_frequency',
            'responsible_person',
            'responsible_person_id',
            'status',
            'effective_date',
            'next_review_date',
            'department',
            'department_name',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'plan_id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class TrendAnalysisListSerializer(serializers.ModelSerializer):
    """List serializer for TrendAnalysis"""

    pms_plan_title = serializers.CharField(
        source='pms_plan.title',
        read_only=True,
    )
    analyzed_by_name = serializers.CharField(
        source='analyzed_by.get_full_name',
        read_only=True,
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )

    class Meta:
        model = TrendAnalysis
        fields = [
            'id',
            'trend_id',
            'pms_plan',
            'pms_plan_title',
            'analysis_period_start',
            'analysis_period_end',
            'product_line',
            'product_line_name',
            'complaint_count',
            'trend_direction',
            'threshold_breached',
            'status',
            'analyzed_by',
            'analyzed_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'trend_id', 'created_at', 'updated_at']


class TrendAnalysisDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for TrendAnalysis"""

    pms_plan_title = serializers.CharField(
        source='pms_plan.title',
        read_only=True,
    )
    analyzed_by = UserSerializer(read_only=True)
    analyzed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='analyzed_by',
        write_only=True,
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )

    class Meta:
        model = TrendAnalysis
        fields = [
            'id',
            'trend_id',
            'pms_plan',
            'pms_plan_title',
            'analysis_period_start',
            'analysis_period_end',
            'product_line',
            'product_line_name',
            'complaint_count',
            'complaint_rate',
            'previous_period_rate',
            'trend_direction',
            'threshold_breached',
            'statistical_method',
            'analysis_summary',
            'key_findings',
            'recommended_actions',
            'analyzed_by',
            'analyzed_by_id',
            'status',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'trend_id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class PMSReportListSerializer(serializers.ModelSerializer):
    """List serializer for PMSReport"""

    pms_plan_title = serializers.CharField(
        source='pms_plan.title',
        read_only=True,
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = PMSReport
        fields = [
            'id',
            'report_id',
            'title',
            'report_type',
            'pms_plan',
            'pms_plan_title',
            'product_line',
            'product_line_name',
            'period_start',
            'period_end',
            'status',
            'submitted_to',
            'submission_date',
            'approved_by',
            'approved_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'report_id', 'created_at', 'updated_at']


class PMSReportDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for PMSReport"""

    pms_plan_title = serializers.CharField(
        source='pms_plan.title',
        read_only=True,
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )
    approved_by = UserSerializer(read_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='approved_by',
        write_only=True,
        required=False,
    )

    class Meta:
        model = PMSReport
        fields = [
            'id',
            'report_id',
            'title',
            'report_type',
            'pms_plan',
            'pms_plan_title',
            'product_line',
            'product_line_name',
            'period_start',
            'period_end',
            'executive_summary',
            'conclusions',
            'recommendations',
            'linked_document',
            'status',
            'submitted_to',
            'submission_date',
            'approved_by',
            'approved_by_id',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'report_id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class VigilanceReportListSerializer(serializers.ModelSerializer):
    """List serializer for VigilanceReport"""

    complaint_id = serializers.CharField(
        source='complaint.complaint_id',
        read_only=True,
    )
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = VigilanceReport
        fields = [
            'id',
            'vigilance_id',
            'complaint',
            'complaint_id',
            'report_form',
            'authority',
            'report_type',
            'submission_deadline',
            'actual_submission_date',
            'tracking_number',
            'patient_outcome',
            'status',
            'submitted_by',
            'submitted_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'vigilance_id', 'created_at', 'updated_at']


class VigilanceReportDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for VigilanceReport"""

    complaint_id = serializers.CharField(
        source='complaint.complaint_id',
        read_only=True,
    )
    submitted_by = UserSerializer(read_only=True)
    submitted_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='submitted_by',
        write_only=True,
        required=False,
    )

    class Meta:
        model = VigilanceReport
        fields = [
            'id',
            'vigilance_id',
            'complaint',
            'complaint_id',
            'report_form',
            'authority',
            'report_type',
            'submission_deadline',
            'actual_submission_date',
            'tracking_number',
            'narrative',
            'patient_outcome',
            'device_udi',
            'lot_number',
            'status',
            'authority_response',
            'response_date',
            'submitted_by',
            'submitted_by_id',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'vigilance_id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class LiteratureReviewListSerializer(serializers.ModelSerializer):
    """List serializer for LiteratureReview"""

    pms_plan_title = serializers.CharField(
        source='pms_plan.title',
        read_only=True,
    )
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = LiteratureReview
        fields = [
            'id',
            'review_id',
            'pms_plan',
            'pms_plan_title',
            'title',
            'search_date',
            'articles_found',
            'articles_relevant',
            'safety_signals_identified',
            'status',
            'reviewed_by',
            'reviewed_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'review_id', 'created_at', 'updated_at']


class LiteratureReviewDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for LiteratureReview"""

    pms_plan_title = serializers.CharField(
        source='pms_plan.title',
        read_only=True,
    )
    reviewed_by = UserSerializer(read_only=True)
    reviewed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewed_by',
        write_only=True,
        required=False,
    )

    class Meta:
        model = LiteratureReview
        fields = [
            'id',
            'review_id',
            'pms_plan',
            'pms_plan_title',
            'title',
            'search_strategy',
            'databases_searched',
            'search_date',
            'articles_found',
            'articles_relevant',
            'key_findings',
            'safety_signals_identified',
            'signal_description',
            'reviewed_by',
            'reviewed_by_id',
            'status',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'review_id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class SafetySignalListSerializer(serializers.ModelSerializer):
    """List serializer for SafetySignal"""

    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )
    evaluated_by_name = serializers.CharField(
        source='evaluated_by.get_full_name',
        read_only=True,
    )

    class Meta:
        model = SafetySignal
        fields = [
            'id',
            'signal_id',
            'title',
            'source',
            'detection_date',
            'product_line',
            'product_line_name',
            'severity',
            'status',
            'evaluated_by',
            'evaluated_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'signal_id', 'created_at', 'updated_at']


class SafetySignalDetailSerializer(serializers.ModelSerializer):
    """Detail serializer for SafetySignal"""

    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
    )
    evaluated_by = UserSerializer(read_only=True)
    evaluated_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='evaluated_by',
        write_only=True,
        required=False,
    )

    class Meta:
        model = SafetySignal
        fields = [
            'id',
            'signal_id',
            'title',
            'description',
            'source',
            'detection_date',
            'product_line',
            'product_line_name',
            'severity',
            'status',
            'evaluation_summary',
            'risk_assessment',
            'action_taken',
            'linked_capa',
            'linked_pms_plan',
            'evaluated_by',
            'evaluated_by_id',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'signal_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
