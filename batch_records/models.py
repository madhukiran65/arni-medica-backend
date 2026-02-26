from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import AuditedModel


class MasterBatchRecord(AuditedModel):
    """
    Master Batch Record - defines the manufacturing process and specifications
    for a batch of products.
    """

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
        ('obsolete', 'Obsolete'),
    )

    mbr_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text='Auto-generated Master Batch Record ID (e.g., MBR-0001)'
    )
    title = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    product_code = models.CharField(max_length=100)
    version = models.CharField(
        max_length=50,
        default='1.0',
        help_text='Version of the master batch record'
    )
    bill_of_materials = models.JSONField(
        default=list,
        help_text='List of materials required for production'
    )
    manufacturing_instructions = models.JSONField(
        default=list,
        help_text='Step-by-step manufacturing process'
    )
    quality_specifications = models.JSONField(
        default=dict,
        help_text='Quality parameters and acceptance criteria'
    )
    linked_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='master_batch_records'
    )
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='master_batch_records'
    )
    effective_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_master_batch_records'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Master Batch Record'
        verbose_name_plural = 'Master Batch Records'
        indexes = [
            models.Index(fields=['mbr_id']),
            models.Index(fields=['product_code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.mbr_id} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.mbr_id:
            # Generate auto ID
            last_record = MasterBatchRecord.objects.order_by('-id').first()
            next_id = (last_record.id if last_record else 0) + 1
            self.mbr_id = f'MBR-{next_id:04d}'
        super().save(*args, **kwargs)

    def approve(self, user):
        """Approve the master batch record."""
        if self.status != 'draft' and self.status != 'in_review':
            raise ValidationError(
                f'Cannot approve a {self.status} master batch record.'
            )
        self.status = 'approved'
        self.approved_by = user
        self.approval_date = timezone.now()
        self.save()

    def supersede(self):
        """Mark this record as superseded."""
        self.status = 'superseded'
        self.save()

    def obsolete(self):
        """Mark this record as obsolete."""
        self.status = 'obsolete'
        self.save()


class BatchRecord(AuditedModel):
    """
    Batch Record - represents an actual manufacturing batch with its production
    history, material usage, and quality data.
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('under_review', 'Under Review'),
        ('released', 'Released'),
        ('rejected', 'Rejected'),
        ('quarantined', 'Quarantined'),
    )

    batch_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text='Auto-generated Batch ID (e.g., BR-0001)'
    )
    batch_number = models.CharField(
        max_length=100,
        unique=True,
        help_text='Unique batch identifier assigned by production'
    )
    lot_number = models.CharField(max_length=100)
    mbr = models.ForeignKey(
        MasterBatchRecord,
        on_delete=models.PROTECT,
        related_name='batch_records'
    )
    quantity_planned = models.IntegerField()
    quantity_produced = models.IntegerField(null=True, blank=True)
    quantity_rejected = models.IntegerField(default=0)
    yield_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Percentage of planned quantity successfully produced'
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    production_line = models.CharField(max_length=100, null=True, blank=True)
    site = models.ForeignKey(
        'users.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batch_records'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_batches'
    )
    released_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='released_batches'
    )
    release_date = models.DateTimeField(null=True, blank=True)
    has_deviations = models.BooleanField(
        default=False,
        help_text='Whether this batch has any deviations'
    )
    review_by_exception = models.BooleanField(
        default=False,
        help_text='Whether this batch requires review by exception'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Batch Record'
        verbose_name_plural = 'Batch Records'
        indexes = [
            models.Index(fields=['batch_id']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['status']),
            models.Index(fields=['lot_number']),
        ]

    def __str__(self):
        return f'{self.batch_id} - {self.batch_number}'

    def save(self, *args, **kwargs):
        if not self.batch_id:
            # Generate auto ID
            last_batch = BatchRecord.objects.order_by('-id').first()
            next_id = (last_batch.id if last_batch else 0) + 1
            self.batch_id = f'BR-{next_id:04d}'

        # Calculate yield percentage if applicable
        if (self.quantity_produced is not None and
            self.quantity_planned and
            self.quantity_planned > 0):
            self.yield_percentage = (
                (self.quantity_produced / self.quantity_planned) * 100
            )

        super().save(*args, **kwargs)

    def start_production(self):
        """Start batch production."""
        if self.status != 'pending':
            raise ValidationError('Only pending batches can be started.')
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()

    def complete_production(self, quantity_produced, quantity_rejected=0):
        """Complete batch production."""
        if self.status != 'in_progress':
            raise ValidationError(
                f'Cannot complete batch with status: {self.status}'
            )
        self.quantity_produced = quantity_produced
        self.quantity_rejected = quantity_rejected
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def submit_for_review(self):
        """Submit batch for review."""
        if self.status != 'completed':
            raise ValidationError(
                'Only completed batches can be submitted for review.'
            )
        self.status = 'under_review'
        self.save()

    def release(self, user):
        """Release the batch."""
        if self.status not in ['under_review', 'completed']:
            raise ValidationError(
                f'Cannot release batch with status: {self.status}'
            )
        self.status = 'released'
        self.released_by = user
        self.release_date = timezone.now()
        self.save()

    def reject(self):
        """Reject the batch."""
        if self.status not in ['under_review', 'completed']:
            raise ValidationError(
                f'Cannot reject batch with status: {self.status}'
            )
        self.status = 'rejected'
        self.save()

    def quarantine(self):
        """Quarantine the batch."""
        self.status = 'quarantined'
        self.save()

    def update_deviation_flag(self):
        """Update the has_deviations flag based on related deviations."""
        self.has_deviations = self.deviations.filter(
            status__in=['open', 'investigating']
        ).exists()
        self.save()


class BatchStep(AuditedModel):
    """
    Batch Step - represents individual steps within a batch production process
    with data collection and verification.
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('deviated', 'Deviated'),
    )

    batch = models.ForeignKey(
        BatchRecord,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    step_number = models.IntegerField()
    instruction_text = models.TextField()
    required_data_fields = models.JSONField(
        default=list,
        help_text='List of data fields required for this step'
    )
    actual_values = models.JSONField(
        default=dict,
        help_text='Collected data values for this step'
    )
    specifications = models.JSONField(
        default=dict,
        help_text='Acceptable parameter ranges'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    requires_verification = models.BooleanField(default=False)
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operated_steps'
    )
    operator_signed_at = models.DateTimeField(null=True, blank=True)
    verifier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_steps'
    )
    verifier_signed_at = models.DateTimeField(null=True, blank=True)
    deviation_notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_within_spec = models.BooleanField(default=True)

    class Meta:
        ordering = ['batch', 'step_number']
        verbose_name = 'Batch Step'
        verbose_name_plural = 'Batch Steps'
        unique_together = ['batch', 'step_number']
        indexes = [
            models.Index(fields=['batch', 'status']),
        ]

    def __str__(self):
        return f'{self.batch.batch_id} - Step {self.step_number}'

    def start_step(self, operator):
        """Start executing the step."""
        if self.status != 'pending':
            raise ValidationError('Only pending steps can be started.')
        self.status = 'in_progress'
        self.operator = operator
        self.started_at = timezone.now()
        self.save()

    def complete_step(self, actual_values):
        """Complete the step with actual values."""
        if self.status != 'in_progress':
            raise ValidationError(
                f'Cannot complete step with status: {self.status}'
            )
        self.actual_values = actual_values
        self.status = 'completed' if self.is_within_spec else 'deviated'
        self.operator_signed_at = timezone.now()
        self.completed_at = timezone.now()
        self.save()

    def verify_step(self, verifier):
        """Verify the completed step."""
        if self.status not in ['completed', 'deviated']:
            raise ValidationError('Only completed steps can be verified.')
        self.verifier = verifier
        self.verifier_signed_at = timezone.now()
        self.save()

    def skip_step(self):
        """Skip the step with justification."""
        self.status = 'skipped'
        self.save()


class BatchDeviation(AuditedModel):
    """
    Batch Deviation - tracks deviations from specifications or procedures
    during batch production.
    """

    DEVIATION_TYPE_CHOICES = (
        ('parameter_excursion', 'Parameter Excursion'),
        ('equipment_failure', 'Equipment Failure'),
        ('material_issue', 'Material Issue'),
        ('process_deviation', 'Process Deviation'),
        ('documentation_error', 'Documentation Error'),
        ('environmental', 'Environmental'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    deviation_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text='Auto-generated Deviation ID (e.g., BD-0001)'
    )
    batch_step = models.ForeignKey(
        BatchStep,
        on_delete=models.CASCADE,
        related_name='deviations',
        null=True,
        blank=True
    )
    batch = models.ForeignKey(
        BatchRecord,
        on_delete=models.CASCADE,
        related_name='deviations'
    )
    deviation_type = models.CharField(
        max_length=50,
        choices=DEVIATION_TYPE_CHOICES
    )
    description = models.TextField()
    impact_assessment = models.TextField(blank=True)
    immediate_action = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    linked_deviation = models.ForeignKey(
        'deviations.Deviation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batch_deviations'
    )
    linked_capa = models.ForeignKey(
        'capa.CAPA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batch_deviations'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_batch_deviations'
    )
    resolution_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Batch Deviation'
        verbose_name_plural = 'Batch Deviations'
        indexes = [
            models.Index(fields=['deviation_id']),
            models.Index(fields=['batch', 'status']),
            models.Index(fields=['deviation_type']),
        ]

    def __str__(self):
        return f'{self.deviation_id} - {self.get_deviation_type_display()}'

    def save(self, *args, **kwargs):
        if not self.deviation_id:
            # Generate auto ID
            last_deviation = BatchDeviation.objects.order_by('-id').first()
            next_id = (last_deviation.id if last_deviation else 0) + 1
            self.deviation_id = f'BD-{next_id:04d}'

        # Update batch deviation flag
        if self.batch:
            self.batch.update_deviation_flag()

        super().save(*args, **kwargs)

    def resolve(self, user):
        """Mark deviation as resolved."""
        if self.status in ['resolved', 'closed']:
            raise ValidationError(
                f'Cannot resolve a {self.status} deviation.'
            )
        self.status = 'resolved'
        self.resolved_by = user
        self.resolution_date = timezone.now()
        self.save()

    def close(self):
        """Close the deviation."""
        if self.status != 'resolved':
            raise ValidationError(
                'Only resolved deviations can be closed.'
            )
        self.status = 'closed'
        self.save()


class BatchMaterial(AuditedModel):
    """
    Batch Material - tracks material usage and consumption during batch
    production.
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('dispensed', 'Dispensed'),
        ('verified', 'Verified'),
        ('consumed', 'Consumed'),
        ('returned', 'Returned'),
    )

    batch = models.ForeignKey(
        BatchRecord,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    material_name = models.CharField(max_length=255)
    material_code = models.CharField(max_length=100)
    lot_number = models.CharField(max_length=100)
    quantity_required = models.DecimalField(max_digits=12, decimal_places=3)
    quantity_used = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True
    )
    unit_of_measure = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    dispensed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispensed_materials'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_materials'
    )

    class Meta:
        ordering = ['batch', 'material_code']
        verbose_name = 'Batch Material'
        verbose_name_plural = 'Batch Materials'
        indexes = [
            models.Index(fields=['batch', 'status']),
            models.Index(fields=['material_code']),
        ]

    def __str__(self):
        return f'{self.batch.batch_id} - {self.material_code}'

    def dispense(self, user):
        """Mark material as dispensed."""
        if self.status != 'pending':
            raise ValidationError(
                f'Cannot dispense material with status: {self.status}'
            )
        self.status = 'dispensed'
        self.dispensed_by = user
        self.save()

    def verify(self, user):
        """Verify the dispensed material."""
        if self.status != 'dispensed':
            raise ValidationError(
                'Only dispensed materials can be verified.'
            )
        self.status = 'verified'
        self.verified_by = user
        self.save()

    def consume(self, quantity_used):
        """Mark material as consumed."""
        if self.status != 'verified':
            raise ValidationError(
                'Only verified materials can be consumed.'
            )
        if quantity_used > self.quantity_required:
            raise ValidationError(
                'Consumed quantity exceeds required quantity.'
            )
        self.quantity_used = quantity_used
        self.status = 'consumed'
        self.save()


class BatchEquipment(AuditedModel):
    """
    Batch Equipment - tracks equipment usage, calibration, and cleaning
    during batch production.
    """

    batch = models.ForeignKey(
        BatchRecord,
        on_delete=models.CASCADE,
        related_name='equipment_usage'
    )
    equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batch_usage'
    )
    equipment_name = models.CharField(max_length=255)
    equipment_id_manual = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Manual equipment ID if not linked to equipment database'
    )
    usage_start = models.DateTimeField(null=True, blank=True)
    usage_end = models.DateTimeField(null=True, blank=True)
    calibration_verified = models.BooleanField(default=False)
    cleaning_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_batch_equipment'
    )

    class Meta:
        ordering = ['batch', 'equipment_name']
        verbose_name = 'Batch Equipment'
        verbose_name_plural = 'Batch Equipment'
        indexes = [
            models.Index(fields=['batch']),
            models.Index(fields=['equipment']),
        ]

    def __str__(self):
        return f'{self.batch.batch_id} - {self.equipment_name}'

    def start_usage(self):
        """Record equipment usage start."""
        self.usage_start = timezone.now()
        self.save()

    def end_usage(self):
        """Record equipment usage end."""
        self.usage_end = timezone.now()
        self.save()

    def verify_calibration(self, user):
        """Mark calibration as verified."""
        self.calibration_verified = True
        self.verified_by = user
        self.save()

    def verify_cleaning(self, user):
        """Mark cleaning as verified."""
        self.cleaning_verified = True
        self.verified_by = user
        self.save()
