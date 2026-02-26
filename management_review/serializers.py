"""
Management Review & Analytics Dashboard Serializers

Comprehensive DRF serializers for all management review models with
list/detail variants for optimized API responses.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    QualityMetric,
    MetricSnapshot,
    QualityObjective,
    ManagementReviewMeeting,
    ManagementReviewItem,
    ManagementReviewAction,
    ManagementReviewReport,
    DashboardConfiguration,
)


# ============================================================================
# QUALITY METRIC SERIALIZERS
# ============================================================================

class QualityMetricListSerializer(serializers.ModelSerializer):
    """Compact serializer for metric lists."""

    class Meta:
        model = QualityMetric
        fields = [
            'id',
            'metric_id',
            'name',
            'module',
            'current_value',
            'unit',
            'threshold_warning',
            'threshold_critical',
            'trend_direction',
            'last_calculated',
        ]
        read_only_fields = ['id', 'metric_id']


class QualityMetricDetailSerializer(serializers.ModelSerializer):
    """Full metric serializer with all details."""

    class Meta:
        model = QualityMetric
        fields = [
            'id',
            'metric_id',
            'name',
            'description',
            'module',
            'calculation_method',
            'query_definition',
            'current_value',
            'threshold_warning',
            'threshold_critical',
            'unit',
            'trend_direction',
            'last_calculated',
            'is_active',
            'display_order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'metric_id', 'created_at', 'updated_at']


# ============================================================================
# METRIC SNAPSHOT SERIALIZERS
# ============================================================================

class MetricSnapshotListSerializer(serializers.ModelSerializer):
    """Compact serializer for snapshot lists."""

    metric_name = serializers.CharField(source='metric.name', read_only=True)

    class Meta:
        model = MetricSnapshot
        fields = [
            'id',
            'metric',
            'metric_name',
            'snapshot_date',
            'value',
            'period_type',
        ]
        read_only_fields = ['id']


class MetricSnapshotDetailSerializer(serializers.ModelSerializer):
    """Full snapshot serializer with details."""

    metric_name = serializers.CharField(source='metric.name', read_only=True)

    class Meta:
        model = MetricSnapshot
        fields = [
            'id',
            'metric',
            'metric_name',
            'snapshot_date',
            'value',
            'period_type',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# QUALITY OBJECTIVE SERIALIZERS
# ============================================================================

class QualityObjectiveListSerializer(serializers.ModelSerializer):
    """Compact serializer for objective lists."""

    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    metric_name = serializers.CharField(source='target_metric.name', read_only=True, allow_null=True)

    class Meta:
        model = QualityObjective
        fields = [
            'id',
            'objective_id',
            'title',
            'target_value',
            'current_value',
            'status',
            'owner_name',
            'department_name',
            'metric_name',
            'target_date',
        ]
        read_only_fields = ['id', 'objective_id']


class QualityObjectiveDetailSerializer(serializers.ModelSerializer):
    """Full objective serializer."""

    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    metric_name = serializers.CharField(source='target_metric.name', read_only=True, allow_null=True)

    class Meta:
        model = QualityObjective
        fields = [
            'id',
            'objective_id',
            'title',
            'description',
            'target_metric',
            'metric_name',
            'target_value',
            'current_value',
            'target_date',
            'status',
            'owner',
            'owner_name',
            'department',
            'department_name',
            'fiscal_year',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'objective_id', 'created_at', 'updated_at']


# ============================================================================
# MANAGEMENT REVIEW MEETING SERIALIZERS
# ============================================================================

class ManagementReviewMeetingListSerializer(serializers.ModelSerializer):
    """Compact serializer for meeting lists."""

    chairperson_name = serializers.CharField(source='chairperson.get_full_name', read_only=True, allow_null=True)
    attendee_count = serializers.SerializerMethodField()

    class Meta:
        model = ManagementReviewMeeting
        fields = [
            'id',
            'meeting_id',
            'title',
            'meeting_type',
            'meeting_date',
            'status',
            'chairperson_name',
            'attendee_count',
            'review_period_start',
            'review_period_end',
        ]
        read_only_fields = ['id', 'meeting_id']

    def get_attendee_count(self, obj):
        return obj.attendees.count()


class ManagementReviewMeetingDetailSerializer(serializers.ModelSerializer):
    """Full meeting serializer with attendees."""

    chairperson_name = serializers.CharField(source='chairperson.get_full_name', read_only=True, allow_null=True)
    attendees_detail = serializers.SerializerMethodField()

    class Meta:
        model = ManagementReviewMeeting
        fields = [
            'id',
            'meeting_id',
            'title',
            'meeting_type',
            'review_period_start',
            'review_period_end',
            'meeting_date',
            'meeting_time',
            'location',
            'chairperson',
            'chairperson_name',
            'attendees',
            'attendees_detail',
            'agenda',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'meeting_id', 'created_at', 'updated_at']

    def get_attendees_detail(self, obj):
        attendees = obj.attendees.all()
        return [{'id': u.id, 'name': u.get_full_name(), 'email': u.email} for u in attendees]


# ============================================================================
# MANAGEMENT REVIEW ITEM SERIALIZERS
# ============================================================================

class ManagementReviewItemListSerializer(serializers.ModelSerializer):
    """Compact serializer for review item lists."""

    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    presenter_name = serializers.CharField(source='presenter.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ManagementReviewItem
        fields = [
            'id',
            'meeting_id',
            'item_number',
            'topic',
            'category',
            'presenter_name',
        ]
        read_only_fields = ['id']


class ManagementReviewItemDetailSerializer(serializers.ModelSerializer):
    """Full item serializer."""

    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    presenter_name = serializers.CharField(source='presenter.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ManagementReviewItem
        fields = [
            'id',
            'meeting',
            'meeting_id',
            'item_number',
            'topic',
            'category',
            'presenter',
            'presenter_name',
            'discussion_summary',
            'data_snapshot',
            'decisions',
            'action_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# MANAGEMENT REVIEW ACTION SERIALIZERS
# ============================================================================

class ManagementReviewActionListSerializer(serializers.ModelSerializer):
    """Compact serializer for action lists."""

    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ManagementReviewAction
        fields = [
            'id',
            'action_id',
            'meeting_id',
            'description',
            'assigned_to_name',
            'due_date',
            'priority',
            'status',
        ]
        read_only_fields = ['id', 'action_id']


class ManagementReviewActionDetailSerializer(serializers.ModelSerializer):
    """Full action serializer."""

    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    capa_id = serializers.CharField(source='linked_capa.capa_id', read_only=True, allow_null=True)
    change_control_id = serializers.CharField(source='linked_change_control.change_control_id', read_only=True, allow_null=True)

    class Meta:
        model = ManagementReviewAction
        fields = [
            'id',
            'action_id',
            'meeting',
            'meeting_id',
            'review_item',
            'description',
            'assigned_to',
            'assigned_to_name',
            'due_date',
            'priority',
            'status',
            'completion_date',
            'completion_notes',
            'linked_capa',
            'capa_id',
            'linked_change_control',
            'change_control_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'action_id', 'created_at', 'updated_at']


# ============================================================================
# MANAGEMENT REVIEW REPORT SERIALIZERS
# ============================================================================

class ManagementReviewReportListSerializer(serializers.ModelSerializer):
    """Compact serializer for report lists."""

    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ManagementReviewReport
        fields = [
            'id',
            'report_id',
            'meeting_id',
            'title',
            'status',
            'overall_quality_assessment',
            'open_actions_count',
            'approved_by_name',
        ]
        read_only_fields = ['id', 'report_id']


class ManagementReviewReportDetailSerializer(serializers.ModelSerializer):
    """Full report serializer."""

    meeting_id = serializers.CharField(source='meeting.meeting_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = ManagementReviewReport
        fields = [
            'id',
            'report_id',
            'meeting',
            'meeting_id',
            'title',
            'executive_summary',
            'key_decisions',
            'open_actions_count',
            'overall_quality_assessment',
            'next_review_date',
            'linked_document',
            'status',
            'approved_by',
            'approved_by_name',
            'approval_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'report_id', 'created_at', 'updated_at']


# ============================================================================
# DASHBOARD CONFIGURATION SERIALIZERS
# ============================================================================

class DashboardConfigurationSerializer(serializers.ModelSerializer):
    """Full dashboard configuration serializer."""

    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True, allow_null=True)
    visible_metrics_detail = serializers.SerializerMethodField()

    class Meta:
        model = DashboardConfiguration
        fields = [
            'id',
            'user',
            'user_name',
            'role',
            'role_name',
            'layout',
            'visible_metrics',
            'visible_metrics_detail',
            'refresh_interval_minutes',
            'theme',
            'filters',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_visible_metrics_detail(self, obj):
        metrics = obj.visible_metrics.all()
        return [{'id': m.id, 'metric_id': m.metric_id, 'name': m.name} for m in metrics]
