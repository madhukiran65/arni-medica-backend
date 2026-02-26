"""
Management Review & Analytics Dashboard Models

Comprehensive models for management review meetings, quality metrics, objectives,
and dashboard analytics - fully integrated with 21 CFR Part 11 compliance via AuditedModel.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import AuditedModel
from users.models import Department


class QualityMetric(AuditedModel):
    """
    Quality metrics that are calculated and tracked over time.
    Supports multiple calculation methods and automated trending.
    """

    MODULE_CHOICES = (
        ('documents', 'Document Control'),
        ('capa', 'CAPA Management'),
        ('complaints', 'Complaint Handling'),
        ('training', 'Training Management'),
        ('deviations', 'Deviation Management'),
        ('change_controls', 'Change Control'),
        ('suppliers', 'Supplier Management'),
        ('audits', 'Audit Management'),
        ('risk_management', 'Risk Management'),
        ('equipment', 'Equipment Management'),
        ('batch_records', 'Batch Records'),
        ('pms', 'Preventive Maintenance'),
    )

    CALCULATION_METHOD_CHOICES = (
        ('count', 'Count'),
        ('average', 'Average'),
        ('percentage', 'Percentage'),
        ('rate', 'Rate'),
        ('sum', 'Sum'),
    )

    TREND_DIRECTION_CHOICES = (
        ('improving', 'Improving'),
        ('declining', 'Declining'),
        ('stable', 'Stable'),
        ('not_applicable', 'Not Applicable'),
    )

    metric_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        help_text="Module where metric is sourced"
    )
    calculation_method = models.CharField(
        max_length=50,
        choices=CALCULATION_METHOD_CHOICES,
        help_text="How the metric is calculated"
    )
    query_definition = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stores the query parameters for auto-calculation (filters, aggregations, etc.)"
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    threshold_warning = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Warning threshold - metric approaching limits"
    )
    threshold_critical = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Critical threshold - immediate action required"
    )
    unit = models.CharField(max_length=20, default='count')
    trend_direction = models.CharField(
        max_length=50,
        choices=TREND_DIRECTION_CHOICES,
        default='not_applicable'
    )
    last_calculated = models.DateTimeField(null=True, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'metric_id']
        verbose_name = 'Quality Metric'
        verbose_name_plural = 'Quality Metrics'
        indexes = [
            models.Index(fields=['metric_id']),
            models.Index(fields=['module']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.metric_id}: {self.name}"

    def save(self, *args, **kwargs):
        """Auto-increment ID via save method if not provided."""
        if not self.metric_id:
            count = QualityMetric.objects.filter(
                metric_id__startswith='QM-'
            ).count()
            self.metric_id = f"QM-{count + 1:04d}"
        super().save(*args, **kwargs)


class MetricSnapshot(AuditedModel):
    """
    Historical snapshots of metrics for trend analysis and reporting.
    """

    PERIOD_TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    )

    metric = models.ForeignKey(
        QualityMetric,
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    snapshot_date = models.DateField(db_index=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    period_type = models.CharField(
        max_length=50,
        choices=PERIOD_TYPE_CHOICES,
        default='monthly'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-snapshot_date']
        verbose_name = 'Metric Snapshot'
        verbose_name_plural = 'Metric Snapshots'
        unique_together = [['metric', 'snapshot_date', 'period_type']]
        indexes = [
            models.Index(fields=['metric', '-snapshot_date']),
            models.Index(fields=['snapshot_date']),
        ]

    def __str__(self):
        return f"{self.metric.name} - {self.snapshot_date}"


class QualityObjective(AuditedModel):
    """
    Quality objectives tracked during management review periods.
    Linked to specific quality metrics and monitored for achievement.
    """

    STATUS_CHOICES = (
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('behind', 'Behind'),
        ('achieved', 'Achieved'),
        ('cancelled', 'Cancelled'),
    )

    objective_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_metric = models.ForeignKey(
        QualityMetric,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='objectives'
    )
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='on_track'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='quality_objectives'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_objectives'
    )
    fiscal_year = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quality Objective'
        verbose_name_plural = 'Quality Objectives'
        indexes = [
            models.Index(fields=['objective_id']),
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return f"{self.objective_id}: {self.title}"

    def save(self, *args, **kwargs):
        """Auto-increment ID via save method if not provided."""
        if not self.objective_id:
            count = QualityObjective.objects.filter(
                objective_id__startswith='QO-'
            ).count()
            self.objective_id = f"QO-{count + 1:04d}"
        super().save(*args, **kwargs)


class ManagementReviewMeeting(AuditedModel):
    """
    Scheduled management review meetings with attendees, agenda, and tracking.
    """

    MEETING_TYPE_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('special', 'Special'),
        ('follow_up', 'Follow-up'),
    )

    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    meeting_id = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    meeting_type = models.CharField(
        max_length=50,
        choices=MEETING_TYPE_CHOICES,
        default='scheduled'
    )
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    meeting_date = models.DateField(db_index=True)
    meeting_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    chairperson = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='chaired_reviews'
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='mr_attendees'
    )
    agenda = models.JSONField(
        default=list,
        blank=True,
        help_text="List of agenda items/topics"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='planned'
    )

    class Meta:
        ordering = ['-meeting_date']
        verbose_name = 'Management Review Meeting'
        verbose_name_plural = 'Management Review Meetings'
        indexes = [
            models.Index(fields=['meeting_id']),
            models.Index(fields=['-meeting_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.meeting_id}: {self.title}"

    def save(self, *args, **kwargs):
        """Auto-increment ID via save method if not provided."""
        if not self.meeting_id:
            count = ManagementReviewMeeting.objects.filter(
                meeting_id__startswith='MRM-'
            ).count()
            self.meeting_id = f"MRM-{count + 1:04d}"
        super().save(*args, **kwargs)


class ManagementReviewItem(AuditedModel):
    """
    Individual agenda items/topics discussed in management review meetings.
    """

    CATEGORY_CHOICES = (
        ('quality_policy', 'Quality Policy & Objectives'),
        ('audit_results', 'Audit Results'),
        ('customer_feedback', 'Customer Feedback'),
        ('process_performance', 'Process Performance'),
        ('product_conformity', 'Product Conformity'),
        ('capa_status', 'CAPA Status'),
        ('changes', 'Changes'),
        ('improvement_opportunities', 'Improvement Opportunities'),
        ('resource_needs', 'Resource Needs'),
        ('supplier_performance', 'Supplier Performance'),
        ('risk_assessment', 'Risk Assessment'),
        ('regulatory_updates', 'Regulatory Updates'),
        ('training_status', 'Training Status'),
    )

    meeting = models.ForeignKey(
        ManagementReviewMeeting,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item_number = models.IntegerField()
    topic = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )
    presenter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='presented_review_items'
    )
    discussion_summary = models.TextField(blank=True)
    data_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of relevant data/metrics for this topic"
    )
    decisions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of decisions made regarding this item"
    )
    action_items = models.JSONField(
        default=list,
        blank=True,
        help_text="List of action items stemming from discussion"
    )

    class Meta:
        ordering = ['meeting', 'item_number']
        verbose_name = 'Management Review Item'
        verbose_name_plural = 'Management Review Items'
        unique_together = [['meeting', 'item_number']]
        indexes = [
            models.Index(fields=['meeting']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.meeting.meeting_id} - Item {self.item_number}: {self.topic}"


class ManagementReviewAction(AuditedModel):
    """
    Action items assigned from management review meetings.
    Tracks assignment, due dates, completion, and links to CAPAs and Change Controls.
    """

    PRIORITY_CHOICES = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    action_id = models.CharField(max_length=50, unique=True, db_index=True)
    meeting = models.ForeignKey(
        ManagementReviewMeeting,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    review_item = models.ForeignKey(
        ManagementReviewItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions'
    )
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_mr_actions'
    )
    due_date = models.DateField(db_index=True)
    priority = models.CharField(
        max_length=50,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='open'
    )
    completion_date = models.DateField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    linked_capa = models.ForeignKey(
        'capa.CAPA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mr_actions'
    )
    linked_change_control = models.ForeignKey(
        'change_controls.ChangeControl',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mr_actions'
    )

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'Management Review Action'
        verbose_name_plural = 'Management Review Actions'
        indexes = [
            models.Index(fields=['action_id']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['-due_date']),
        ]

    def __str__(self):
        return f"{self.action_id}: {self.description[:50]}"

    def save(self, *args, **kwargs):
        """Auto-increment ID via save method if not provided."""
        if not self.action_id:
            count = ManagementReviewAction.objects.filter(
                action_id__startswith='MRA-'
            ).count()
            self.action_id = f"MRA-{count + 1:04d}"
        super().save(*args, **kwargs)


class ManagementReviewReport(AuditedModel):
    """
    Formal management review report generated from a meeting.
    OneToOneField to meeting to ensure only one report per meeting.
    """

    QUALITY_ASSESSMENT_CHOICES = (
        ('excellent', 'Excellent'),
        ('satisfactory', 'Satisfactory'),
        ('needs_improvement', 'Needs Improvement'),
        ('unsatisfactory', 'Unsatisfactory'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
    )

    report_id = models.CharField(max_length=50, unique=True, db_index=True)
    meeting = models.OneToOneField(
        ManagementReviewMeeting,
        on_delete=models.CASCADE,
        related_name='report'
    )
    title = models.CharField(max_length=255)
    executive_summary = models.TextField()
    key_decisions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of key decisions from the meeting"
    )
    open_actions_count = models.IntegerField(default=0)
    overall_quality_assessment = models.CharField(
        max_length=50,
        choices=QUALITY_ASSESSMENT_CHOICES,
        default='satisfactory'
    )
    next_review_date = models.DateField(null=True, blank=True)
    linked_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mr_reports'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_mr_reports'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Management Review Report'
        verbose_name_plural = 'Management Review Reports'
        indexes = [
            models.Index(fields=['report_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.report_id}: {self.title}"

    def save(self, *args, **kwargs):
        """Auto-increment ID via save method if not provided."""
        if not self.report_id:
            count = ManagementReviewReport.objects.filter(
                report_id__startswith='MRR-'
            ).count()
            self.report_id = f"MRR-{count + 1:04d}"
        super().save(*args, **kwargs)


class DashboardConfiguration(AuditedModel):
    """
    Per-user dashboard configuration for customizing analytics views.
    OneToOneField ensures one config per user.
    """

    THEME_CHOICES = (
        ('default', 'Default'),
        ('compact', 'Compact'),
        ('expanded', 'Expanded'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_config'
    )
    role = models.ForeignKey(
        'users.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    layout = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom layout configuration (widget positions, sizes, etc.)"
    )
    visible_metrics = models.ManyToManyField(
        QualityMetric,
        blank=True,
        related_name='dashboard_configs'
    )
    refresh_interval_minutes = models.IntegerField(
        default=30,
        help_text="Auto-refresh interval in minutes"
    )
    theme = models.CharField(
        max_length=50,
        choices=THEME_CHOICES,
        default='default'
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Saved filter configurations"
    )

    class Meta:
        verbose_name = 'Dashboard Configuration'
        verbose_name_plural = 'Dashboard Configurations'

    def __str__(self):
        return f"Dashboard config for {self.user.get_full_name()}"
