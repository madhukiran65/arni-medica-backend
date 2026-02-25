from django.db import models
from django.contrib.auth.models import User


class AuditedModel(models.Model):
    """Base model with audit trail"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True


class AuditPlan(AuditedModel):
    AUDIT_TYPE_CHOICES = (
        ('internal', 'Internal'),
        ('supplier', 'Supplier'),
    )

    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    )

    audit_id = models.CharField(max_length=50, unique=True)
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPE_CHOICES)
    scope = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    lead_auditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_plans_led')
    supplier = models.CharField(max_length=255, blank=True)
    findings_count = models.IntegerField(default=0)
    major_nc = models.IntegerField(default=0)
    minor_nc = models.IntegerField(default=0)
    observations = models.IntegerField(default=0)
    next_audit_planned = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Plan'
        verbose_name_plural = 'Audit Plans'

    def __str__(self):
        return f"{self.audit_id} - {self.get_audit_type_display()}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate audit_id."""
        if not self.audit_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'AUD'
            last = AuditPlan.objects.filter(audit_id__startswith=f'{prefix}-{year}-').order_by('-audit_id').first()
            if last and getattr(last, 'audit_id'):
                try:
                    seq = int(getattr(last, 'audit_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.audit_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)

    def update_findings_count(self):
        """Update findings count from related findings"""
        self.findings_count = self.findings.count()
        self.major_nc = self.findings.filter(category='major_nc').count()
        self.minor_nc = self.findings.filter(category='minor_nc').count()
        self.observations = self.findings.filter(category='observation').count()
        self.save()


class AuditFinding(AuditedModel):
    CATEGORY_CHOICES = (
        ('major_nc', 'Major Non-Conformance'),
        ('minor_nc', 'Minor Non-Conformance'),
        ('observation', 'Observation'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('capa_assigned', 'CAPA Assigned'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    audit = models.ForeignKey(AuditPlan, on_delete=models.CASCADE, related_name='findings')
    finding_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    evidence = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_capa = models.ForeignKey('capa.CAPA', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_findings')
    target_closure_date = models.DateField(null=True, blank=True)
    actual_closure_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Finding'
        verbose_name_plural = 'Audit Findings'

    def __str__(self):
        return f"{self.finding_id} - {self.get_category_display()}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate finding_id."""
        if not self.finding_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'FND'
            last = AuditFinding.objects.filter(finding_id__startswith=f'{prefix}-{year}-').order_by('-finding_id').first()
            if last and getattr(last, 'finding_id'):
                try:
                    seq = int(getattr(last, 'finding_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.finding_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)
