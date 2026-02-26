from django.db import models
from django.conf import settings
from core.models import AuditedModel
from users.models import Department


class Supplier(AuditedModel):
    """Supplier information and qualification status."""
    
    SUPPLIER_TYPE_CHOICES = [
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('service_provider', 'Service Provider'),
        ('raw_material', 'Raw Material Supplier'),
        ('component', 'Component Supplier'),
        ('calibration', 'Calibration Service'),
        ('sterilization', 'Sterilization Service'),
        ('other', 'Other'),
    ]
    
    QUALIFICATION_STATUS_CHOICES = [
        ('not_qualified', 'Not Qualified'),
        ('pending_evaluation', 'Pending Evaluation'),
        ('pending_audit', 'Pending Audit'),
        ('qualified', 'Qualified'),
        ('conditionally_qualified', 'Conditionally Qualified'),
        ('suspended', 'Suspended'),
        ('disqualified', 'Disqualified'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    # Basic Information
    supplier_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    supplier_type = models.CharField(max_length=50, choices=SUPPLIER_TYPE_CHOICES)
    
    # Contact Information
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    website = models.URLField(null=True, blank=True)
    
    # Qualification
    qualification_status = models.CharField(
        max_length=30,
        choices=QUALIFICATION_STATUS_CHOICES,
        default='not_qualified'
    )
    qualified_date = models.DateField(null=True, blank=True)
    next_evaluation_date = models.DateField(null=True, blank=True)
    qualification_notes = models.TextField(blank=True)
    
    # Risk Assessment
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='medium')
    risk_justification = models.TextField(blank=True)
    
    # Compliance
    iso_certified = models.BooleanField(default=False)
    iso_certificate_number = models.CharField(max_length=100, blank=True)
    iso_expiry_date = models.DateField(null=True, blank=True)
    regulatory_registrations = models.JSONField(blank=True, null=True)
    gmp_compliant = models.BooleanField(default=False)
    
    # Products/Services
    products_services = models.JSONField(blank=True, null=True)
    approved_materials = models.JSONField(blank=True, null=True)
    portal_access_enabled = models.BooleanField(
        default=False,
        help_text="Supplier can access supplier portal"
    )
    portal_email = models.EmailField(
        null=True,
        blank=True,
        help_text="Portal login email for supplier"
    )
    auto_quarantine_on_cert_expiry = models.BooleanField(
        default=True,
        help_text="Automatically quarantine supplier on certificate expiry"
    )
    approved_scope = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="e.g., Approved for packaging only"
    )
    supplier_category = models.CharField(
        max_length=30,
        choices=(
            ('drug_component', 'Drug Component'),
            ('device_component', 'Device Component'),
            ('packaging', 'Packaging'),
            ('service', 'Service'),
            ('raw_material', 'Raw Material'),
            ('other', 'Other')
        ),
        default='other',
        blank=True,
        help_text="Supplier category"
    )

    # Relations
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suppliers'
    )
    quality_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_suppliers'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        indexes = [
            models.Index(fields=['supplier_id']),
            models.Index(fields=['qualification_status', 'risk_level']),
            models.Index(fields=['department', 'qualification_status']),
            models.Index(fields=['supplier_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.supplier_id})"

    def save(self, *args, **kwargs):
        """Override save to auto-generate supplier_id."""
        if not self.supplier_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'SUP'
            last = Supplier.objects.filter(supplier_id__startswith=f'{prefix}-{year}-').order_by('-supplier_id').first()
            if last and getattr(last, 'supplier_id'):
                try:
                    seq = int(getattr(last, 'supplier_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.supplier_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


class SupplierEvaluation(AuditedModel):
    """Supplier evaluation and scoring records."""
    
    EVALUATION_TYPE_CHOICES = [
        ('initial', 'Initial Evaluation'),
        ('periodic', 'Periodic Evaluation'),
        ('for_cause', 'For Cause Evaluation'),
        ('re_evaluation', 'Re-evaluation'),
    ]
    
    RECOMMENDATION_CHOICES = [
        ('approve', 'Approve'),
        ('conditionally_approve', 'Conditionally Approve'),
        ('reject', 'Reject'),
        ('re_evaluate', 'Re-evaluate'),
    ]
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    evaluation_date = models.DateField()
    evaluation_type = models.CharField(max_length=30, choices=EVALUATION_TYPE_CHOICES)
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    delivery_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    service_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supplier_evaluations'
    )
    comments = models.TextField(blank=True)
    recommendation = models.CharField(max_length=30, choices=RECOMMENDATION_CHOICES)
    next_evaluation_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-evaluation_date']
        verbose_name = 'Supplier Evaluation'
        verbose_name_plural = 'Supplier Evaluations'
        indexes = [
            models.Index(fields=['supplier', 'evaluation_date']),
            models.Index(fields=['evaluation_type']),
        ]
    
    def __str__(self):
        return f"{self.supplier.name} - {self.get_evaluation_type_display()} ({self.evaluation_date})"


class SupplierDocument(models.Model):
    """Supporting documents for suppliers (certificates, agreements, etc)."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('quality_agreement', 'Quality Agreement'),
        ('certificate', 'Certificate'),
        ('audit_report', 'Audit Report'),
        ('corrective_action', 'Corrective Action'),
        ('other', 'Other'),
    ]
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='supplier_documents/%Y/%m/')
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_supplier_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Supplier Document'
        verbose_name_plural = 'Supplier Documents'
        indexes = [
            models.Index(fields=['supplier', 'document_type']),
        ]
    
    def __str__(self):
        return f"{self.supplier.name} - {self.title}"


class SupplierCorrectiveAction(AuditedModel):
    """Corrective actions (SCAR) for suppliers."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending_response', 'Pending Response'),
        ('response_received', 'Response Received'),
        ('verified', 'Verified'),
        ('closed', 'Closed'),
    ]
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='corrective_actions'
    )
    issue_description = models.TextField()
    scar_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    response_due_date = models.DateField()
    response_received_date = models.DateField(null=True, blank=True)
    corrective_action = models.TextField(blank=True)
    verification_result = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_supplier_actions'
    )
    capa = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference to CAPA (Corrective & Preventive Action) module'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Supplier Corrective Action'
        verbose_name_plural = 'Supplier Corrective Actions'
        indexes = [
            models.Index(fields=['supplier', 'status']),
            models.Index(fields=['scar_number']),
            models.Index(fields=['response_due_date']),
        ]
    
    def __str__(self):
        return f"{self.scar_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate scar_number."""
        if not self.scar_number:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'SCAR'
            last = SupplierCorrectiveAction.objects.filter(scar_number__startswith=f'{prefix}-{year}-').order_by('-scar_number').first()
            if last and getattr(last, 'scar_number'):
                try:
                    seq = int(getattr(last, 'scar_number').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.scar_number = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)
