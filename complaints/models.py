from django.db import models
from django.utils import timezone
from core.models import AuditedModel
from users.models import Department
from django.conf import settings


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
