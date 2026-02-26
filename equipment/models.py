from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from core.models import AuditedModel


class Equipment(AuditedModel):
    EQUIPMENT_TYPE_CHOICES = (
        ('manufacturing', 'Manufacturing'),
        ('laboratory', 'Laboratory'),
        ('testing', 'Testing'),
        ('packaging', 'Packaging'),
        ('utility', 'Utility'),
        ('it_system', 'IT System'),
    )

    CATEGORY_CHOICES = (
        ('direct_product_contact', 'Direct Product Contact'),
        ('indirect_product_contact', 'Indirect Product Contact'),
        ('facility', 'Facility'),
        ('calibrated_instrument', 'Calibrated Instrument'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('quarantined', 'Quarantined'),
        ('out_of_service', 'Out of Service'),
        ('decommissioned', 'Decommissioned'),
        ('pending_qualification', 'Pending Qualification'),
    )

    CRITICALITY_CHOICES = (
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
    )

    equipment_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    serial_number = models.CharField(max_length=100, unique=True)
    model_number = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    site = models.ForeignKey('users.Site', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('users.Department', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending_qualification')
    criticality = models.CharField(max_length=10, choices=CRITICALITY_CHOICES, default='minor')
    purchase_date = models.DateField(null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    requires_calibration = models.BooleanField(default=False)
    requires_maintenance = models.BooleanField(default=True)
    qr_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['equipment_id']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.equipment_id} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.equipment_id:
            last_equipment = Equipment.objects.all().order_by('id').last()
            if last_equipment and last_equipment.equipment_id:
                try:
                    last_number = int(last_equipment.equipment_id.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.equipment_id = f"EQ-{new_number:04d}"
        super().save(*args, **kwargs)


class EquipmentQualification(AuditedModel):
    QUALIFICATION_TYPE_CHOICES = (
        ('iq', 'Installation Qualification (IQ)'),
        ('oq', 'Operational Qualification (OQ)'),
        ('pq', 'Performance Qualification (PQ)'),
        ('requalification', 'Requalification'),
    )

    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional'),
        ('not_executed', 'Not Executed'),
    )

    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    qualification_id = models.CharField(max_length=20, unique=True, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='qualifications')
    qualification_type = models.CharField(max_length=20, choices=QUALIFICATION_TYPE_CHOICES)
    protocol_number = models.CharField(max_length=100, blank=True)
    protocol_file = models.FileField(upload_to='equipment/protocols/', null=True, blank=True)
    result_file = models.FileField(upload_to='equipment/results/', null=True, blank=True)
    execution_date = models.DateField(null=True, blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='not_executed')
    deviations_noted = models.TextField(blank=True)
    qualified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='qualified_equipment')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_qualifications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['qualification_id']),
            models.Index(fields=['equipment', 'qualification_type']),
        ]

    def __str__(self):
        return f"{self.qualification_id} - {self.equipment.name} ({self.get_qualification_type_display()})"

    def save(self, *args, **kwargs):
        if not self.qualification_id:
            last_qualification = EquipmentQualification.objects.all().order_by('id').last()
            if last_qualification and last_qualification.qualification_id:
                try:
                    last_number = int(last_qualification.qualification_id.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.qualification_id = f"EQQ-{new_number:04d}"
        super().save(*args, **kwargs)


class CalibrationSchedule(AuditedModel):
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, related_name='calibration_schedule')
    interval_days = models.IntegerField(validators=[MinValueValidator(1)])
    tolerance_specs = models.JSONField(default=dict, blank=True)
    calibration_method = models.CharField(max_length=255, blank=True)
    reference_standards = models.CharField(max_length=500, blank=True)
    last_calibrated = models.DateField(null=True, blank=True)
    next_due = models.DateField(null=True, blank=True)
    auto_quarantine_on_overdue = models.BooleanField(default=True)
    reminder_days_before = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['next_due']
        indexes = [
            models.Index(fields=['next_due']),
            models.Index(fields=['equipment']),
        ]

    def __str__(self):
        return f"Calibration Schedule - {self.equipment.name} (Next Due: {self.next_due})"

    def is_overdue(self):
        if self.next_due:
            return timezone.now().date() > self.next_due
        return False

    def days_until_due(self):
        if self.next_due:
            delta = self.next_due - timezone.now().date()
            return delta.days
        return None


class CalibrationRecord(AuditedModel):
    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('adjusted_pass', 'Adjusted Pass'),
        ('out_of_tolerance', 'Out of Tolerance'),
    )

    CALIBRATION_TYPE_CHOICES = (
        ('internal', 'Internal'),
        ('external', 'External'),
    )

    calibration_id = models.CharField(max_length=20, unique=True, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='calibration_records')
    calibration_date = models.DateField()
    as_found_data = models.JSONField(default=dict, blank=True)
    as_left_data = models.JSONField(default=dict, blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    certificate_number = models.CharField(max_length=100, blank=True)
    certificate_file = models.FileField(upload_to='equipment/certificates/', null=True, blank=True)
    performed_by_internal = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='internal_calibrations')
    performed_by_vendor = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_calibrations')
    calibration_type = models.CharField(max_length=10, choices=CALIBRATION_TYPE_CHOICES)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_calibrations')
    notes = models.TextField(blank=True)
    linked_deviation = models.ForeignKey('deviations.Deviation', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-calibration_date']
        indexes = [
            models.Index(fields=['calibration_id']),
            models.Index(fields=['equipment', '-calibration_date']),
            models.Index(fields=['result']),
        ]

    def __str__(self):
        return f"{self.calibration_id} - {self.equipment.name} ({self.calibration_date})"

    def save(self, *args, **kwargs):
        if not self.calibration_id:
            last_record = CalibrationRecord.objects.all().order_by('id').last()
            if last_record and last_record.calibration_id:
                try:
                    last_number = int(last_record.calibration_id.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.calibration_id = f"CAL-{new_number:04d}"
        super().save(*args, **kwargs)


class MaintenanceSchedule(AuditedModel):
    MAINTENANCE_TYPE_CHOICES = (
        ('preventive', 'Preventive'),
        ('predictive', 'Predictive'),
    )

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    interval_days = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    last_performed = models.DateField(null=True, blank=True)
    next_due = models.DateField(null=True, blank=True)
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['next_due']
        indexes = [
            models.Index(fields=['equipment', 'maintenance_type']),
            models.Index(fields=['next_due']),
        ]

    def __str__(self):
        return f"{self.get_maintenance_type_display()} - {self.equipment.name}"

    def is_overdue(self):
        if self.next_due:
            return timezone.now().date() > self.next_due
        return False


class MaintenanceRecord(AuditedModel):
    MAINTENANCE_TYPE_CHOICES = (
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
        ('predictive', 'Predictive'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    maintenance_id = models.CharField(max_length=20, unique=True, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    work_performed = models.TextField(blank=True)
    parts_replaced = models.JSONField(default=list, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    downtime_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    linked_deviation = models.ForeignKey('deviations.Deviation', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-maintenance_date']
        indexes = [
            models.Index(fields=['maintenance_id']),
            models.Index(fields=['equipment', '-maintenance_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.maintenance_id} - {self.equipment.name} ({self.maintenance_date})"

    def save(self, *args, **kwargs):
        if not self.maintenance_id:
            last_record = MaintenanceRecord.objects.all().order_by('id').last()
            if last_record and last_record.maintenance_id:
                try:
                    last_number = int(last_record.maintenance_id.split('-')[1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            self.maintenance_id = f"MR-{new_number:04d}"
        super().save(*args, **kwargs)


class EquipmentDocument(AuditedModel):
    DOCUMENT_TYPE_CHOICES = (
        ('manual', 'Equipment Manual'),
        ('sop', 'Standard Operating Procedure'),
        ('calibration_cert', 'Calibration Certificate'),
        ('qualification_report', 'Qualification Report'),
        ('maintenance_log', 'Maintenance Log'),
        ('spare_parts_list', 'Spare Parts List'),
    )

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='equipment/documents/')
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['equipment', 'document_type']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.equipment.name}"

    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False
