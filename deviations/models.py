from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import AuditedModel
from users.models import Department


class Deviation(AuditedModel):
    """8-stage workflow for deviation management"""
    
    # Stage choices
    STAGE_OPENED = 'opened'
    STAGE_QA_REVIEW = 'qa_review'
    STAGE_INVESTIGATION = 'investigation'
    STAGE_CAPA_PLAN = 'capa_plan'
    STAGE_PENDING_CAPA_APPROVAL = 'pending_capa_approval'
    STAGE_PENDING_CAPA_COMPLETION = 'pending_capa_completion'
    STAGE_PENDING_FINAL_APPROVAL = 'pending_final_approval'
    STAGE_COMPLETED = 'completed'
    
    STAGE_CHOICES = [
        (STAGE_OPENED, 'Opened'),
        (STAGE_QA_REVIEW, 'QA Review'),
        (STAGE_INVESTIGATION, 'Investigation'),
        (STAGE_CAPA_PLAN, 'CAPA Plan'),
        (STAGE_PENDING_CAPA_APPROVAL, 'Pending CAPA Approval'),
        (STAGE_PENDING_CAPA_COMPLETION, 'Pending CAPA Completion'),
        (STAGE_PENDING_FINAL_APPROVAL, 'Pending Final Approval'),
        (STAGE_COMPLETED, 'Completed'),
    ]
    
    # Type choices
    TYPE_PLANNED = 'planned'
    TYPE_UNPLANNED = 'unplanned'
    
    TYPE_CHOICES = [
        (TYPE_PLANNED, 'Planned'),
        (TYPE_UNPLANNED, 'Unplanned'),
    ]
    
    # Category choices
    CATEGORY_PRODUCT = 'product'
    CATEGORY_PROCESS = 'process'
    CATEGORY_SYSTEM = 'system'
    CATEGORY_DOCUMENTATION = 'documentation'
    CATEGORY_EQUIPMENT = 'equipment'
    CATEGORY_MATERIAL = 'material'
    CATEGORY_ENVIRONMENTAL = 'environmental'
    CATEGORY_OTHER = 'other'
    
    CATEGORY_CHOICES = [
        (CATEGORY_PRODUCT, 'Product'),
        (CATEGORY_PROCESS, 'Process'),
        (CATEGORY_SYSTEM, 'System'),
        (CATEGORY_DOCUMENTATION, 'Documentation'),
        (CATEGORY_EQUIPMENT, 'Equipment'),
        (CATEGORY_MATERIAL, 'Material'),
        (CATEGORY_ENVIRONMENTAL, 'Environmental'),
        (CATEGORY_OTHER, 'Other'),
    ]
    
    # Severity choices
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_MAJOR = 'major'
    SEVERITY_MINOR = 'minor'
    SEVERITY_OBSERVATION = 'observation'
    
    SEVERITY_CHOICES = [
        (SEVERITY_CRITICAL, 'Critical'),
        (SEVERITY_MAJOR, 'Major'),
        (SEVERITY_MINOR, 'Minor'),
        (SEVERITY_OBSERVATION, 'Observation'),
    ]
    
    # Source choices
    SOURCE_PRODUCTION = 'production'
    SOURCE_LABORATORY = 'laboratory'
    SOURCE_WAREHOUSE = 'warehouse'
    SOURCE_INCOMING_INSPECTION = 'incoming_inspection'
    SOURCE_CUSTOMER_COMPLAINT = 'customer_complaint'
    SOURCE_AUDIT_FINDING = 'audit_finding'
    SOURCE_SELF_INSPECTION = 'self_inspection'
    SOURCE_OTHER = 'other'
    
    SOURCE_CHOICES = [
        (SOURCE_PRODUCTION, 'Production'),
        (SOURCE_LABORATORY, 'Laboratory'),
        (SOURCE_WAREHOUSE, 'Warehouse'),
        (SOURCE_INCOMING_INSPECTION, 'Incoming Inspection'),
        (SOURCE_CUSTOMER_COMPLAINT, 'Customer Complaint'),
        (SOURCE_AUDIT_FINDING, 'Audit Finding'),
        (SOURCE_SELF_INSPECTION, 'Self Inspection'),
        (SOURCE_OTHER, 'Other'),
    ]
    
    # Disposition choices
    DISPOSITION_USE_AS_IS = 'use_as_is'
    DISPOSITION_REWORK = 'rework'
    DISPOSITION_REJECT = 'reject'
    DISPOSITION_RETURN_TO_SUPPLIER = 'return_to_supplier'
    DISPOSITION_SCRAP = 'scrap'
    DISPOSITION_OTHER = 'other'
    
    DISPOSITION_CHOICES = [
        (DISPOSITION_USE_AS_IS, 'Use As Is'),
        (DISPOSITION_REWORK, 'Rework'),
        (DISPOSITION_REJECT, 'Reject'),
        (DISPOSITION_RETURN_TO_SUPPLIER, 'Return to Supplier'),
        (DISPOSITION_SCRAP, 'Scrap'),
        (DISPOSITION_OTHER, 'Other'),
    ]
    
    # Identification
    deviation_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text='Auto-generated ID in format DEV-YYYY-NNNN'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Classification
    deviation_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    # Source
    source = models.CharField(max_length=25, choices=SOURCE_CHOICES)
    source_reference = models.TextField(blank=True, null=True)
    
    # Impact
    process_affected = models.TextField()
    product_affected = models.TextField()
    batch_lot_number = models.CharField(max_length=100, blank=True, null=True)
    quantity_affected = models.IntegerField(blank=True, null=True)
    impact_assessment = models.TextField()
    patient_safety_impact = models.BooleanField(default=False)
    
    # Stage tracking
    current_stage = models.CharField(
        max_length=30,
        choices=STAGE_CHOICES,
        default=STAGE_OPENED
    )
    stage_entered_at = models.DateTimeField(auto_now_add=True)
    
    # Investigation
    root_cause = models.TextField(blank=True, null=True)
    investigation_summary = models.TextField(blank=True, null=True)
    investigated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deviations_investigated'
    )
    investigation_completed_at = models.DateTimeField(blank=True, null=True)
    
    # Resolution
    corrective_action = models.TextField(blank=True, null=True)
    preventive_action = models.TextField(blank=True, null=True)
    capa = models.ForeignKey(
        'capa.CAPA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deviations'
    )
    disposition = models.CharField(
        max_length=25,
        choices=DISPOSITION_CHOICES,
        blank=True,
        null=True
    )
    disposition_justification = models.TextField(blank=True, null=True)
    
    # Dates & SLA
    reported_date = models.DateTimeField(default=timezone.now)
    target_closure_date = models.DateTimeField(blank=True, null=True)
    actual_closure_date = models.DateTimeField(blank=True, null=True)
    
    # Assignment
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='deviations'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='deviations_reported'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deviations_assigned'
    )
    qa_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deviations_reviewed'
    )
    
    # Flags
    requires_capa = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    regulatory_reportable = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-reported_date']
        indexes = [
            models.Index(fields=['deviation_id']),
            models.Index(fields=['current_stage']),
            models.Index(fields=['severity']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f'{self.deviation_id} - {self.title}'
    
    @property
    def days_open(self):
        """Calculate the number of days the deviation has been open"""
        end_date = self.actual_closure_date or timezone.now()
        delta = end_date - self.reported_date
        return delta.days

    def save(self, *args, **kwargs):
        """Override save to auto-generate deviation_id."""
        if not self.deviation_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'DEV'
            last = Deviation.objects.filter(deviation_id__startswith=f'{prefix}-{year}-').order_by('-deviation_id').first()
            if last and getattr(last, 'deviation_id'):
                try:
                    seq = int(getattr(last, 'deviation_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.deviation_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


class DeviationAttachment(models.Model):
    """File attachments for deviations"""
    
    deviation = models.ForeignKey(
        Deviation,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='deviations/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()  # in bytes
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='deviation_attachments_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f'{self.deviation.deviation_id} - {self.file_name}'


class DeviationComment(models.Model):
    """Threaded comments on deviations"""
    
    deviation = models.ForeignKey(
        Deviation,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='deviation_comments'
    )
    comment = models.TextField()
    stage = models.CharField(
        max_length=30,
        choices=Deviation.STAGE_CHOICES,
        blank=True,
        null=True,
        help_text='Stage at which this comment was made'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author} on {self.deviation.deviation_id}'
