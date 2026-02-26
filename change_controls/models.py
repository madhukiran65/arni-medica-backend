from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import AuditedModel
from users.models import Department


class ChangeControl(AuditedModel):
    """
    Comprehensive change control model implementing a 7-stage workflow for managing
    changes to documents, processes, systems, equipment, and other controlled items
    in a regulated environment.
    """

    # Change Type Choices
    CHANGE_TYPE_CHOICES = [
        ('document', 'Document Change'),
        ('process', 'Process Change'),
        ('system', 'System Change'),
        ('equipment', 'Equipment Change'),
        ('supplier', 'Supplier Change'),
        ('material', 'Material Change'),
        ('facility', 'Facility Change'),
        ('software', 'Software Change'),
        ('personnel', 'Personnel Change'),
        ('regulatory', 'Regulatory Change'),
    ]

    # Change Category Choices
    CHANGE_CATEGORY_CHOICES = [
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('emergency', 'Emergency'),
    ]

    # Risk Level Choices
    RISK_LEVEL_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    # Workflow Stage Choices
    STAGE_CHOICES = [
        ('submitted', 'Submitted'),
        ('screening', 'Screening'),
        ('impact_assessment', 'Impact Assessment'),
        ('approval', 'Approval'),
        ('implementation', 'Implementation'),
        ('verification', 'Verification'),
        ('closed', 'Closed'),
    ]

    # Identification Section
    change_control_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated identifier in format CC-YYYY-NNNN"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Classification Section
    change_type = models.CharField(max_length=50, choices=CHANGE_TYPE_CHOICES)
    change_category = models.CharField(max_length=50, choices=CHANGE_CATEGORY_CHOICES)
    risk_level = models.CharField(max_length=50, choices=RISK_LEVEL_CHOICES)

    # Stage Section
    current_stage = models.CharField(
        max_length=50,
        choices=STAGE_CHOICES,
        default='submitted'
    )
    stage_entered_at = models.DateTimeField(default=timezone.now)

    # Scope Section
    affected_areas = models.JSONField(
        default=list,
        blank=True,
        help_text="List of affected areas"
    )
    affected_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of affected document IDs"
    )
    affected_processes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of affected processes"
    )
    affected_products = models.JSONField(
        default=list,
        blank=True,
        help_text="List of affected products"
    )
    affected_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='change_controls'
    )

    # Impact Assessment Section
    impact_summary = models.TextField(blank=True)
    quality_impact = models.TextField(blank=True)
    regulatory_impact = models.TextField(blank=True)
    safety_impact = models.TextField(blank=True)
    training_impact = models.BooleanField(default=False)
    validation_impact = models.BooleanField(default=False)
    documentation_impact = models.BooleanField(default=False)

    # Planning Section
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_controls_proposed'
    )
    justification = models.TextField(blank=True)
    proposed_implementation_date = models.DateTimeField(null=True, blank=True)
    actual_implementation_date = models.DateTimeField(null=True, blank=True)
    rollback_plan = models.TextField(blank=True)

    # Verification Section
    verification_method = models.TextField(blank=True)
    verification_results = models.TextField(blank=True)
    verification_completed = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_controls_verified'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Assignment Section
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_controls_assigned'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_change_controls'
    )
    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sponsored_change_controls',
        help_text="Management sponsor for the change"
    )

    # Linked Records
    related_capa = models.ForeignKey(
        'capa.CAPA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_controls'
    )
    related_deviation = models.ForeignKey(
        'deviations.Deviation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_controls'
    )

    # Dates Section
    submitted_date = models.DateTimeField(default=timezone.now)
    target_completion_date = models.DateTimeField(null=True, blank=True)
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_change_controls'
    )

    # Flags
    requires_validation = models.BooleanField(default=False)
    requires_regulatory_notification = models.BooleanField(default=False)
    is_emergency = models.BooleanField(default=False)
    impact_assessment_checklist = models.JSONField(
        default=dict,
        blank=True,
        help_text="Checklist: requires_revalidation, risk_file_update, regulatory_submission, training"
    )
    regulatory_submission_required = models.BooleanField(
        default=False,
        help_text="Whether regulatory submission is required"
    )
    regulatory_submission_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Type of regulatory submission (e.g., 510k, PMA)"
    )
    regulatory_submission_status = models.CharField(
        max_length=20,
        choices=(
            ('not_required', 'Not Required'),
            ('pending', 'Pending'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved')
        ),
        default='not_required',
        blank=True,
        help_text="Status of regulatory submission"
    )
    effectiveness_check_required = models.BooleanField(
        default=False,
        help_text="Whether post-implementation effectiveness check is required"
    )
    effectiveness_check_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled date for effectiveness check"
    )
    effectiveness_check_result = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('effective', 'Effective'),
            ('not_effective', 'Not Effective')
        ),
        default='pending',
        blank=True,
        help_text="Result of effectiveness check"
    )
    all_child_tasks_complete = models.BooleanField(
        default=False,
        help_text="All child implementation tasks are complete"
    )

    class Meta:
        ordering = ['-submitted_date']
        indexes = [
            models.Index(fields=['change_control_id']),
            models.Index(fields=['current_stage']),
            models.Index(fields=['change_type']),
            models.Index(fields=['change_category']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['submitted_date']),
            models.Index(fields=['department']),
        ]
        verbose_name = 'Change Control'
        verbose_name_plural = 'Change Controls'

    def __str__(self):
        return f"{self.change_control_id}: {self.title}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate change_control_id."""
        if not self.change_control_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'CC'
            last = ChangeControl.objects.filter(change_control_id__startswith=f'{prefix}-{year}-').order_by('-change_control_id').first()
            if last and getattr(last, 'change_control_id'):
                try:
                    seq = int(getattr(last, 'change_control_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.change_control_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


class ChangeControlApproval(AuditedModel):
    """
    Tracks approvals for change controls through the approval workflow.
    """

    APPROVAL_ROLE_CHOICES = [
        ('department_head', 'Department Head'),
        ('qa_manager', 'QA Manager'),
        ('regulatory', 'Regulatory Affairs'),
        ('management', 'Management'),
        ('technical', 'Technical Expert'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    ]

    change_control = models.ForeignKey(
        ChangeControl,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='change_control_approvals'
    )
    approval_role = models.CharField(max_length=50, choices=APPROVAL_ROLE_CHOICES)
    sequence = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    signature = models.ForeignKey(
        'core.ElectronicSignature',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_control_approvals'
    )

    class Meta:
        ordering = ['sequence', 'created_at']
        unique_together = ['change_control', 'approver']
        verbose_name = 'Change Control Approval'
        verbose_name_plural = 'Change Control Approvals'

    def __str__(self):
        return f"{self.change_control.change_control_id} - {self.approver} ({self.status})"


class ChangeControlTask(AuditedModel):
    """
    Represents implementation tasks for a change control.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    change_control = models.ForeignKey(
        ChangeControl,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_change_control_tasks'
    )
    due_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    sequence = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['sequence', 'due_date']
        verbose_name = 'Change Control Task'
        verbose_name_plural = 'Change Control Tasks'

    def __str__(self):
        return f"{self.change_control.change_control_id} - Task {self.sequence}: {self.title}"


class ChangeControlAttachment(models.Model):
    """
    File attachments for change controls.
    """

    change_control = models.ForeignKey(
        ChangeControl,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='change_controls/attachments/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_control_attachments_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Change Control Attachment'
        verbose_name_plural = 'Change Control Attachments'

    def __str__(self):
        return f"{self.change_control.change_control_id} - {self.file_name}"


class ChangeControlComment(models.Model):
    """
    Comments/notes on change controls with support for nested threaded comments.
    """

    change_control = models.ForeignKey(
        ChangeControl,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_control_comments'
    )
    comment = models.TextField()
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
        verbose_name = 'Change Control Comment'
        verbose_name_plural = 'Change Control Comments'

    def __str__(self):
        return f"{self.change_control.change_control_id} - Comment by {self.author}"
