"""
Management Review & Analytics Dashboard Admin Configuration

Comprehensive Django admin interface for all management review models
with read-only audit fields and custom actions.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
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


@admin.register(QualityMetric)
class QualityMetricAdmin(admin.ModelAdmin):
    """Admin interface for Quality Metrics."""

    list_display = (
        'metric_id',
        'name',
        'module',
        'calculation_method',
        'current_value',
        'unit',
        'trend_color',
        'is_active',
    )
    list_filter = (
        'module',
        'calculation_method',
        'trend_direction',
        'is_active',
        'created_at',
    )
    search_fields = ('metric_id', 'name', 'description')
    readonly_fields = (
        'metric_id',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('Identification', {
            'fields': ('metric_id', 'name', 'description')
        }),
        ('Configuration', {
            'fields': (
                'module',
                'calculation_method',
                'query_definition',
                'unit',
            )
        }),
        ('Values', {
            'fields': (
                'current_value',
                'threshold_warning',
                'threshold_critical',
                'trend_direction',
            )
        }),
        ('Tracking', {
            'fields': (
                'last_calculated',
                'display_order',
                'is_active',
            )
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('display_order', 'metric_id')

    def trend_color(self, obj):
        """Display trend direction with color coding."""
        colors = {
            'improving': '#28a745',
            'declining': '#dc3545',
            'stable': '#ffc107',
            'not_applicable': '#6c757d',
        }
        color = colors.get(obj.trend_direction, '#6c757d')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color,
            obj.get_trend_direction_display()
        )
    trend_color.short_description = 'Trend'


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    """Admin interface for Metric Snapshots."""

    list_display = ('metric', 'snapshot_date', 'period_type', 'value', 'created_at')
    list_filter = ('period_type', 'snapshot_date', 'metric__module')
    search_fields = ('metric__metric_id', 'metric__name', 'notes')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    fieldsets = (
        ('Snapshot', {
            'fields': ('metric', 'snapshot_date', 'value', 'period_type')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-snapshot_date',)
    date_hierarchy = 'snapshot_date'


@admin.register(QualityObjective)
class QualityObjectiveAdmin(admin.ModelAdmin):
    """Admin interface for Quality Objectives."""

    list_display = (
        'objective_id',
        'title',
        'owner',
        'status_badge',
        'target_date',
        'fiscal_year',
    )
    list_filter = (
        'status',
        'fiscal_year',
        'department',
        'owner',
        'target_date',
    )
    search_fields = ('objective_id', 'title', 'description')
    readonly_fields = (
        'objective_id',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('Identification', {
            'fields': ('objective_id', 'title', 'description')
        }),
        ('Targets', {
            'fields': (
                'target_metric',
                'target_value',
                'current_value',
                'target_date',
            )
        }),
        ('Ownership', {
            'fields': ('owner', 'department', 'fiscal_year')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'on_track': '#28a745',
            'at_risk': '#ffc107',
            'behind': '#dc3545',
            'achieved': '#007bff',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


class ManagementReviewItemInline(admin.TabularInline):
    """Inline admin for review items."""

    model = ManagementReviewItem
    extra = 0
    fields = ('item_number', 'topic', 'category', 'presenter')
    ordering = ('item_number',)



@admin.register(ManagementReviewMeeting)
class ManagementReviewMeetingAdmin(admin.ModelAdmin):
    """Admin interface for Management Review Meetings."""

    list_display = (
        'meeting_id',
        'title',
        'meeting_date',
        'status_badge',
        'chairperson',
        'item_count',
    )
    list_filter = (
        'status',
        'meeting_type',
        'meeting_date',
        'chairperson',
    )
    search_fields = ('meeting_id', 'title')
    readonly_fields = (
        'meeting_id',
        'item_count',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('Identification', {
            'fields': ('meeting_id', 'title', 'meeting_type')
        }),
        ('Schedule', {
            'fields': (
                'review_period_start',
                'review_period_end',
                'meeting_date',
                'meeting_time',
                'location',
            )
        }),
        ('Participants', {
            'fields': ('chairperson', 'attendees')
        }),
        ('Content', {
            'fields': ('agenda',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Summary', {
            'fields': ('item_count',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-meeting_date',)
    filter_horizontal = ('attendees',)

    def item_count(self, obj):
        """Display count of review items."""
        count = obj.items.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    item_count.short_description = 'Items'

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'planned': '#007bff',
            'in_progress': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


class ManagementReviewItemAdmin(admin.ModelAdmin):
    """Admin interface for Management Review Items."""

    list_display = (
        'meeting_id_link',
        'item_number',
        'topic',
        'category',
        'presenter',
    )
    list_filter = ('category', 'meeting__meeting_date')
    search_fields = ('topic', 'meeting__meeting_id', 'discussion_summary')
    readonly_fields = (
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('Meeting Item', {
            'fields': ('meeting', 'item_number', 'topic', 'category')
        }),
        ('Content', {
            'fields': (
                'presenter',
                'discussion_summary',
                'data_snapshot',
                'decisions',
                'action_items',
            )
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('meeting', 'item_number')

    def meeting_id_link(self, obj):
        return obj.meeting.meeting_id
    meeting_id_link.short_description = 'Meeting'


@admin.register(ManagementReviewAction)
class ManagementReviewActionAdmin(admin.ModelAdmin):
    """Admin interface for Management Review Actions."""

    list_display = (
        'action_id',
        'description_short',
        'assigned_to',
        'due_date',
        'priority_badge',
        'status_badge',
    )
    list_filter = (
        'status',
        'priority',
        'due_date',
        'assigned_to',
    )
    search_fields = ('action_id', 'description')
    readonly_fields = (
        'action_id',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('Identification', {
            'fields': ('action_id', 'description')
        }),
        ('Assignment', {
            'fields': ('meeting', 'review_item', 'assigned_to')
        }),
        ('Timeline', {
            'fields': ('due_date', 'completion_date')
        }),
        ('Status', {
            'fields': ('priority', 'status', 'completion_notes')
        }),
        ('Linkages', {
            'fields': ('linked_capa', 'linked_change_control')
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-due_date',)

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

    def priority_badge(self, obj):
        """Display priority with color coding."""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'open': '#007bff',
            'in_progress': '#ffc107',
            'completed': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ManagementReviewReport)
class ManagementReviewReportAdmin(admin.ModelAdmin):
    """Admin interface for Management Review Reports."""

    list_display = (
        'report_id',
        'title',
        'meeting_link',
        'status_badge',
        'quality_assessment_badge',
        'approved_by',
    )
    list_filter = (
        'status',
        'overall_quality_assessment',
        'approval_date',
        'approved_by',
    )
    search_fields = ('report_id', 'title', 'executive_summary')
    readonly_fields = (
        'report_id',
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('Identification', {
            'fields': ('report_id', 'title', 'meeting')
        }),
        ('Content', {
            'fields': (
                'executive_summary',
                'key_decisions',
                'open_actions_count',
            )
        }),
        ('Assessment', {
            'fields': ('overall_quality_assessment', 'next_review_date')
        }),
        ('Linkages', {
            'fields': ('linked_document',)
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approval_date')
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)

    def meeting_link(self, obj):
        return obj.meeting.meeting_id
    meeting_link.short_description = 'Meeting'

    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'draft': '#6c757d',
            'in_review': '#ffc107',
            'approved': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def quality_assessment_badge(self, obj):
        """Display quality assessment with color coding."""
        colors = {
            'excellent': '#28a745',
            'satisfactory': '#007bff',
            'needs_improvement': '#ffc107',
            'unsatisfactory': '#dc3545',
        }
        color = colors.get(obj.overall_quality_assessment, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_overall_quality_assessment_display()
        )
    quality_assessment_badge.short_description = 'Quality Assessment'


@admin.register(DashboardConfiguration)
class DashboardConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for Dashboard Configurations."""

    list_display = (
        'user_name',
        'role_name',
        'theme',
        'refresh_interval_minutes',
        'metric_count',
    )
    list_filter = ('theme', 'refresh_interval_minutes', 'role')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = (
        'created_by',
        'created_at',
        'updated_by',
        'updated_at',
    )
    fieldsets = (
        ('User', {
            'fields': ('user', 'role')
        }),
        ('Display', {
            'fields': ('layout', 'theme', 'refresh_interval_minutes')
        }),
        ('Metrics', {
            'fields': ('visible_metrics',)
        }),
        ('Filters', {
            'fields': ('filters',)
        }),
        ('Audit Trail', {
            'fields': (
                'created_by',
                'created_at',
                'updated_by',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('visible_metrics',)

    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'User'

    def role_name(self, obj):
        return obj.role.name if obj.role else '—'
    role_name.short_description = 'Role'

    def metric_count(self, obj):
        count = obj.visible_metrics.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            count
        )
    metric_count.short_description = 'Metrics'
