from django.db import models
from django.utils import timezone
from core.models import AuditedModel
from users.models import Department
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Complaint(AuditedModel):
    """
    Enhanced Complaint model with FDA 3500A MDR reporting capabilities.
    Supports complete complaint lifecycle from receipt through investigation,
    CAPA initiation, and FDA reportability determination.
    """
    
    # Status workflow
    STATUS_CHOICES = (
        ('new', 'New'),
        ('under_investigation', 'Under Investigation'),
        ('capa_initiated', 'CAPA Initiated'),
        ('investigation_complete', 'Investigation Complete'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    )
    
    # Complainant type
    COMPLAINANT_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('patient', 'Patient'),
        ('healthcare_provider', 'Healthcare Provider'),
        ('distributor', 'Distributor'),
        ('internal', 'Internal'),
        ('regulatory_authority', 'Regulatory Authority'),
        ('other', 'Other'),
    )
    
    # Classification categories
    CATEGORY_CHOICES = (
        ('product_quality', 'Product Quality'),
        ('product_performance', 'Product Performance'),
        ('labeling', 'Labeling'),
        ('packaging', 'Packaging'),
        ('documentation', 'Documentation'),
        ('service', 'Service'),
        ('other', 'Other'),
    )
    
    # Severity levels
    SEVERITY_CHOICES = (
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
    )
    
    # Priority levels
    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    
    # FDA 3500A Event Type
    EVENT_TYPE_CHOICES = (
        ('death', 'Death'),
        ('serious_injury', 'Serious Injury'),
        ('malfunction', 'Malfunction'),
        ('other', 'Other'),
        ('none', 'None'),
    )
    
    # Patient sex
    PATIENT_SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknown', 'Unknown'),
    )
    
    # Device usage
    DEVICE_USAGE_CHOICES = (
        ('initial_use', 'Initial Use'),
        ('reuse', 'Reuse'),
        ('unknown', 'Unknown'),
    )
    
    # Device availability
    DEVICE_AVAILABLE_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('returned_to_manufacturer', 'Returned to Manufacturer'),
        ('unknown', 'Unknown'),
    )
    
    # MDR Submission Status
    MDR_SUBMISSION_STATUS_CHOICES = (
        ('not_required', 'Not Required'),
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('follow_up_required', 'Follow-up Required'),
    )
    
    # MDR Report Type
    MDR_REPORT_TYPE_CHOICES = (
        ('initial', 'Initial'),
        ('follow_up', 'Follow-up'),
        ('supplemental', 'Supplemental'),
    )
    
    # Identification
    complaint_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Auto-generated identifier: CMP-YYYY-NNNN"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed complaint description")
    
    # Status & Workflow
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True
    )
    stage_entered_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when complaint entered current status"
    )
    
    # Complainant Information
    complainant_name = models.CharField(max_length=255)
    complainant_email = models.EmailField()
    complainant_phone = models.CharField(max_length=20, blank=True)
    complainant_organization = models.CharField(max_length=255, blank=True)
    complainant_type = models.CharField(
        max_length=30,
        choices=COMPLAINANT_TYPE_CHOICES
    )
    
    # Product Information
    product_name = models.CharField(max_length=255)
    product_code = models.CharField(max_length=100)
    product_lot_number = models.CharField(max_length=100, blank=True)
    product_serial_number = models.CharField(max_length=100, blank=True)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    product_description = models.TextField(blank=True)
    
    # Event Details
    event_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the complaint event occurred"
    )
    event_description = models.TextField()
    event_location = models.CharField(max_length=255)
    event_country = models.CharField(max_length=100)
    sample_available = models.BooleanField(default=False)
    sample_received_date = models.DateField(null=True, blank=True)
    
    # Classification
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES
    )
    
    # FDA 3500A Fields
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        default='none',
        db_index=True,
        help_text="FDA 3500A event type classification"
    )
    patient_age = models.IntegerField(
        null=True,
        blank=True,
        help_text="Patient age in years"
    )
    patient_sex = models.CharField(
        max_length=20,
        choices=PATIENT_SEX_CHOICES,
        null=True,
        blank=True
    )
    patient_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Patient weight in kilograms"
    )
    health_effect = models.TextField(
        blank=True,
        help_text="Description of health effect reported"
    )
    device_usage = models.CharField(
        max_length=20,
        choices=DEVICE_USAGE_CHOICES,
        null=True,
        blank=True
    )
    device_available = models.CharField(
        max_length=30,
        choices=DEVICE_AVAILABLE_CHOICES,
        null=True,
        blank=True
    )
    
    # Reportability
    is_reportable_to_fda = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this complaint meets FDA reportability criteria"
    )
    reportability_determination_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date reportability decision was made"
    )
    reportability_justification = models.TextField(
        blank=True,
        help_text="Explanation of reportability determination"
    )
    reportability_determined_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportability_determinations'
    )
    awareness_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date manufacturer became aware of the event"
    )
    
    # MDR Submission
    mdr_report_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="FDA assigned MDR report number"
    )
    mdr_submission_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date MDR was submitted to FDA"
    )
    mdr_submission_status = models.CharField(
        max_length=30,
        choices=MDR_SUBMISSION_STATUS_CHOICES,
        default='not_required',
        help_text="Current MDR submission status"
    )
    mdr_report_type = models.CharField(
        max_length=20,
        choices=MDR_REPORT_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Type of MDR report (initial, follow-up, supplemental)"
    )
    fda_reference_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="FDA reference or tracking number"
    )
    
    # Investigation
    investigation_summary = models.TextField(
        blank=True,
        help_text="Summary of investigation findings"
    )
    root_cause = models.TextField(
        blank=True,
        help_text="Root cause analysis"
    )
    investigation_completed_date = models.DateField(
        null=True,
        blank=True
    )
    investigated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaint_investigations'
    )
    
    # Resolution
    resolution_description = models.TextField(
        blank=True,
        help_text="Description of how complaint was resolved"
    )
    capa = models.ForeignKey(
        'capa.CAPA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )
    corrective_action = models.TextField(
        blank=True,
        help_text="Corrective action(s) taken"
    )
    preventive_action = models.TextField(
        blank=True,
        help_text="Preventive action(s) to avoid recurrence"
    )
    
    # Assignment
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='complaints'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_complaints',
        help_text="Complaint coordinator"
    )
    
    # Dates
    received_date = models.DateTimeField(
        default=timezone.now,
        help_text="When complaint was received"
    )
    target_closure_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date for closure"
    )
    actual_closure_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date when complaint was closed"
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_complaints'
    )
    
    # Flags
    is_trending = models.BooleanField(
        default=False,
        help_text="Whether this complaint is part of a trend"
    )
    trend_category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category if part of a trend"
    )
    requires_field_action = models.BooleanField(
        default=False,
        help_text="Whether field action is required"
    )
    reportability_decision_tree = models.JSONField(
        default=dict,
        blank=True,
        help_text="Decision tree answers for reportability determination"
    )
    auto_generated_form = models.CharField(
        max_length=50,
        choices=(
            ('fda_3500a', 'FDA 3500A'),
            ('fda_3500', 'FDA 3500'),
            ('emdr', 'eMDR'),
            ('mir', 'MIR'),
            ('none', 'None')
        ),
        default='none',
        blank=True,
        help_text="Auto-generated regulatory form type"
    )
    affected_lot_numbers = models.JSONField(
        default=list,
        blank=True,
        help_text="List of affected lot/batch numbers"
    )
    quarantine_triggered = models.BooleanField(
        default=False,
        help_text="Whether product quarantine was initiated"
    )
    pms_linked = models.BooleanField(
        default=False,
        help_text="Linked to PMS (Post-Market Surveillance) trend analysis"
    )
    patient_follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether patient follow-up is required"
    )
    patient_follow_up_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('na', 'N/A')
        ),
        default='na',
        blank=True,
        help_text="Status of patient follow-up"
    )
    
    class Meta:
        ordering = ['-received_date']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        indexes = [
            models.Index(fields=['complaint_id']),
            models.Index(fields=['status']),
            models.Index(fields=['severity']),
            models.Index(fields=['event_type']),
            models.Index(fields=['is_reportable_to_fda']),
            models.Index(fields=['mdr_submission_status']),
            models.Index(fields=['received_date']),
        ]
    
    def __str__(self):
        return f"{self.complaint_id} - {self.product_name}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate complaint_id."""
        if not self.complaint_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'CMP'
            last = Complaint.objects.filter(complaint_id__startswith=f'{prefix}-{year}-').order_by('-complaint_id').first()
            if last and getattr(last, 'complaint_id'):
                try:
                    seq = int(getattr(last, 'complaint_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.complaint_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


class ComplaintAttachment(models.Model):
    """Files and documents associated with complaints"""
    
    ATTACHMENT_TYPE_CHOICES = (
        ('investigation_report', 'Investigation Report'),
        ('fda_3500a', 'FDA 3500A Form'),
        ('fda_3500h', 'FDA 3500H Form'),
        ('customer_correspondence', 'Customer Correspondence'),
        ('photo', 'Photo'),
        ('lab_result', 'Lab Result'),
        ('other', 'Other'),
    )
    
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='complaints/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    attachment_type = models.CharField(
        max_length=30,
        choices=ATTACHMENT_TYPE_CHOICES
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='complaint_attachments'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Complaint Attachment'
        verbose_name_plural = 'Complaint Attachments'
    
    def __str__(self):
        return f"{self.complaint.complaint_id} - {self.file_name}"


class MIRRecord(AuditedModel):
    """
    Medical Incident Report (MIR) for FDA follow-ups and supplemental reports.
    Tracks relationship between multiple MDR submissions for the same event.
    """
    
    REPORT_TYPE_CHOICES = (
        ('initial', 'Initial'),
        ('follow_up', 'Follow-up'),
        ('supplemental', 'Supplemental'),
    )
    
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='mir_records'
    )
    mir_number = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique MIR identifier"
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES
    )
    parent_mir = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='follow_up_records',
        help_text="Reference to parent MIR if this is a follow-up"
    )
    submitted_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date MIR was submitted to FDA"
    )
    submitted_to = models.CharField(
        max_length=255,
        blank=True,
        help_text="FDA office or address MIR was submitted to"
    )
    narrative = models.TextField(
        help_text="Narrative description for this MIR"
    )
    patient_outcome = models.TextField(
        blank=True,
        help_text="Patient outcome information"
    )
    device_evaluation_summary = models.TextField(
        blank=True,
        help_text="Summary of device evaluation findings"
    )
    
    class Meta:
        ordering = ['-submitted_date']
        verbose_name = 'MIR Record'
        verbose_name_plural = 'MIR Records'
    
    def __str__(self):
        return f"{self.mir_number} - {self.report_type}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate mir_number."""
        if not self.mir_number:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'MIR'
            last = MIRRecord.objects.filter(mir_number__startswith=f'{prefix}-{year}-').order_by('-mir_number').first()
            if last and getattr(last, 'mir_number'):
                try:
                    seq = int(getattr(last, 'mir_number').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.mir_number = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


class ComplaintComment(models.Model):
    """Threaded comments for complaint discussion and collaboration"""
    
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaint_comments'
    )
    comment = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment if this is a reply"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Complaint Comment'
        verbose_name_plural = 'Complaint Comments'
    
    def __str__(self):
        return f"{self.complaint.complaint_id} - Comment by {self.author.username}"


# ============================================================================
# PMS (Post-Market Surveillance) Models - Merged from pms app
# ============================================================================


class PMSPlan(AuditedModel):
    """Post-Market Surveillance Plan"""

    REVIEW_FREQUENCY_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('closed', 'Closed'),
    )

    plan_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    plan_version = models.CharField(max_length=50)
    data_sources = models.JSONField(
        default=list,
        help_text='List of data sources: complaints, literature, clinical, service',
    )
    monitoring_criteria = models.TextField()
    review_frequency = models.CharField(
        max_length=20,
        choices=REVIEW_FREQUENCY_CHOICES,
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pms_plans',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
    )
    effective_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        'users.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['plan_id']),
            models.Index(fields=['status']),
            models.Index(fields=['product_line']),
        ]

    def __str__(self):
        return f"{self.plan_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.plan_id:
            last_plan = PMSPlan.objects.filter(
                plan_id__startswith='PMS-'
            ).order_by('-created_at').first()
            if last_plan:
                last_num = int(last_plan.plan_id.split('-')[1])
                self.plan_id = f"PMS-{last_num + 1:04d}"
            else:
                self.plan_id = "PMS-0001"
        super().save(*args, **kwargs)


class TrendAnalysis(AuditedModel):
    """Trend Analysis for surveillance data"""

    TREND_DIRECTION_CHOICES = (
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing'),
        ('stable', 'Stable'),
        ('insufficient_data', 'Insufficient Data'),
    )

    STATISTICAL_METHOD_CHOICES = (
        ('control_chart', 'Control Chart'),
        ('pareto', 'Pareto'),
        ('regression', 'Regression'),
        ('chi_square', 'Chi-Square'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('action_required', 'Action Required'),
    )

    trend_id = models.CharField(max_length=50, unique=True, editable=False)
    pms_plan = models.ForeignKey(
        PMSPlan,
        on_delete=models.CASCADE,
        related_name='trend_analyses',
    )
    analysis_period_start = models.DateField()
    analysis_period_end = models.DateField()
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    complaint_count = models.IntegerField(default=0)
    complaint_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )
    previous_period_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )
    trend_direction = models.CharField(
        max_length=20,
        choices=TREND_DIRECTION_CHOICES,
    )
    threshold_breached = models.BooleanField(default=False)
    statistical_method = models.CharField(
        max_length=20,
        choices=STATISTICAL_METHOD_CHOICES,
    )
    analysis_summary = models.TextField()
    key_findings = models.JSONField(default=list)
    recommended_actions = models.JSONField(default=list)
    analyzed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trend_analyses',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trend_id']),
            models.Index(fields=['pms_plan']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.trend_id} - {self.pms_plan.title}"

    def save(self, *args, **kwargs):
        if not self.trend_id:
            last_analysis = TrendAnalysis.objects.filter(
                trend_id__startswith='TA-'
            ).order_by('-created_at').first()
            if last_analysis:
                last_num = int(last_analysis.trend_id.split('-')[1])
                self.trend_id = f"TA-{last_num + 1:04d}"
            else:
                self.trend_id = "TA-0001"
        super().save(*args, **kwargs)


class PMSReport(AuditedModel):
    """Post-Market Surveillance Report"""

    REPORT_TYPE_CHOICES = (
        ('pms_report', 'PMS Report'),
        ('psur', 'PSUR'),
        ('pmcf_report', 'PMCF Report'),
        ('pms_update', 'PMS Update'),
        ('sscp', 'SSCP'),
        ('trend_report', 'Trend Report'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('submitted', 'Submitted'),
    )

    SUBMITTED_TO_CHOICES = (
        ('fda', 'FDA'),
        ('ema', 'EMA'),
        ('cdsco', 'CDSCO'),
        ('notified_body', 'Notified Body'),
        ('internal', 'Internal'),
        ('other', 'Other'),
    )

    report_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
    )
    pms_plan = models.ForeignKey(
        PMSPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
    )
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    period_start = models.DateField()
    period_end = models.DateField()
    executive_summary = models.TextField()
    conclusions = models.TextField()
    recommendations = models.TextField()
    linked_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
    )
    submitted_to = models.CharField(
        max_length=20,
        choices=SUBMITTED_TO_CHOICES,
        null=True,
        blank=True,
    )
    submission_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_pms_reports',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_id']),
            models.Index(fields=['status']),
            models.Index(fields=['report_type']),
        ]

    def __str__(self):
        return f"{self.report_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.report_id:
            last_report = PMSReport.objects.filter(
                report_id__startswith='PMSR-'
            ).order_by('-created_at').first()
            if last_report:
                last_num = int(last_report.report_id.split('-')[1])
                self.report_id = f"PMSR-{last_num + 1:04d}"
            else:
                self.report_id = "PMSR-0001"
        super().save(*args, **kwargs)


class VigilanceReport(AuditedModel):
    """Vigilance Report for regulatory submission"""

    REPORT_FORM_CHOICES = (
        ('fda_3500a', 'FDA 3500A'),
        ('fda_3500', 'FDA 3500'),
        ('emdr', 'EMDR'),
        ('mir', 'MIR'),
        ('field_safety_notice', 'Field Safety Notice'),
        ('field_safety_corrective_action', 'Field Safety Corrective Action'),
    )

    AUTHORITY_CHOICES = (
        ('fda', 'FDA'),
        ('ema', 'EMA'),
        ('cdsco', 'CDSCO'),
        ('tga', 'TGA'),
        ('health_canada', 'Health Canada'),
        ('mhra', 'MHRA'),
        ('other', 'Other'),
    )

    REPORT_TYPE_CHOICES = (
        ('initial', 'Initial'),
        ('followup', 'Follow-up'),
        ('final', 'Final'),
    )

    PATIENT_OUTCOME_CHOICES = (
        ('death', 'Death'),
        ('life_threatening', 'Life Threatening'),
        ('hospitalization', 'Hospitalization'),
        ('disability', 'Disability'),
        ('congenital_anomaly', 'Congenital Anomaly'),
        ('intervention_required', 'Intervention Required'),
        ('other', 'Other'),
        ('unknown', 'Unknown'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_submission', 'Pending Submission'),
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('closed', 'Closed'),
    )

    vigilance_id = models.CharField(max_length=50, unique=True, editable=False)
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='vigilance_reports',
    )
    report_form = models.CharField(
        max_length=30,
        choices=REPORT_FORM_CHOICES,
    )
    authority = models.CharField(
        max_length=20,
        choices=AUTHORITY_CHOICES,
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
    )
    submission_deadline = models.DateField()
    actual_submission_date = models.DateField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    narrative = models.TextField()
    patient_outcome = models.CharField(
        max_length=25,
        choices=PATIENT_OUTCOME_CHOICES,
        null=True,
        blank=True,
    )
    device_udi = models.CharField(max_length=100, null=True, blank=True)
    lot_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
    )
    authority_response = models.TextField(blank=True)
    response_date = models.DateField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vigilance_reports',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vigilance_id']),
            models.Index(fields=['status']),
            models.Index(fields=['authority']),
        ]

    def __str__(self):
        return f"{self.vigilance_id} - {self.get_authority_display()}"

    def save(self, *args, **kwargs):
        if not self.vigilance_id:
            last_vigilance = VigilanceReport.objects.filter(
                vigilance_id__startswith='VR-'
            ).order_by('-created_at').first()
            if last_vigilance:
                last_num = int(last_vigilance.vigilance_id.split('-')[1])
                self.vigilance_id = f"VR-{last_num + 1:04d}"
            else:
                self.vigilance_id = "VR-0001"
        super().save(*args, **kwargs)


class LiteratureReview(AuditedModel):
    """Literature Review for surveillance"""

    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('action_required', 'Action Required'),
    )

    review_id = models.CharField(max_length=50, unique=True, editable=False)
    pms_plan = models.ForeignKey(
        PMSPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='literature_reviews',
    )
    title = models.CharField(max_length=255)
    search_strategy = models.TextField()
    databases_searched = models.JSONField(default=list)
    search_date = models.DateField()
    articles_found = models.IntegerField(default=0)
    articles_relevant = models.IntegerField(default=0)
    key_findings = models.JSONField(default=list)
    safety_signals_identified = models.BooleanField(default=False)
    signal_description = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='literature_reviews',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['review_id']),
            models.Index(fields=['status']),
            models.Index(fields=['pms_plan']),
        ]

    def __str__(self):
        return f"{self.review_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.review_id:
            last_review = LiteratureReview.objects.filter(
                review_id__startswith='LR-'
            ).order_by('-created_at').first()
            if last_review:
                last_num = int(last_review.review_id.split('-')[1])
                self.review_id = f"LR-{last_num + 1:04d}"
            else:
                self.review_id = "LR-0001"
        super().save(*args, **kwargs)


class SafetySignal(AuditedModel):
    """Safety Signal detection and management"""

    SOURCE_CHOICES = (
        ('complaints', 'Complaints'),
        ('literature', 'Literature'),
        ('clinical_data', 'Clinical Data'),
        ('registry', 'Registry'),
        ('proactive_monitoring', 'Proactive Monitoring'),
    )

    SEVERITY_CHOICES = (
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
    )

    STATUS_CHOICES = (
        ('detected', 'Detected'),
        ('under_evaluation', 'Under Evaluation'),
        ('confirmed', 'Confirmed'),
        ('refuted', 'Refuted'),
        ('closed', 'Closed'),
    )

    signal_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    source = models.CharField(
        max_length=25,
        choices=SOURCE_CHOICES,
    )
    detection_date = models.DateField()
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_signals',
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='detected',
    )
    evaluation_summary = models.TextField(blank=True)
    risk_assessment = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    linked_capa = models.ForeignKey(
        'capa.CAPA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_signals',
    )
    linked_pms_plan = models.ForeignKey(
        PMSPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_signals',
    )
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_signals_evaluated',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['signal_id']),
            models.Index(fields=['status']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"{self.signal_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.signal_id:
            last_signal = SafetySignal.objects.filter(
                signal_id__startswith='SS-'
            ).order_by('-created_at').first()
            if last_signal:
                last_num = int(last_signal.signal_id.split('-')[1])
                self.signal_id = f"SS-{last_num + 1:04d}"
            else:
                self.signal_id = "SS-0001"
        super().save(*args, **kwargs)
