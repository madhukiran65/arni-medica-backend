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


class Complaint(AuditedModel):
    SEVERITY_CHOICES = (
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
    )

    STATUS_CHOICES = (
        ('new', 'New'),
        ('under_investigation', 'Under Investigation'),
        ('capa_initiated', 'CAPA Initiated'),
        ('investigation_complete', 'Investigation Complete'),
        ('closed', 'Closed'),
    )

    REPORTABLE_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('under_review', 'Under Review'),
    )

    complaint_id = models.CharField(max_length=50, unique=True)
    product = models.CharField(max_length=255)
    batch_lot = models.CharField(max_length=100, blank=True)
    customer = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    reportable = models.CharField(max_length=20, choices=REPORTABLE_CHOICES, default='under_review')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_assigned')
    complaint_date = models.DateField()
    investigation_summary = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    impact_assessment = models.TextField(blank=True)
    related_capa = models.ForeignKey('capa.CAPA', on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    ai_triage = models.TextField(blank=True)
    ai_confidence = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'

    def __str__(self):
        return f"{self.complaint_id} - {self.product}"


class ComplaintInvestigation(AuditedModel):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='investigations')
    investigator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='complaint_investigations')
    investigation_step = models.CharField(max_length=255)
    findings = models.TextField()
    investigation_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-investigation_date']
        verbose_name = 'Complaint Investigation'
        verbose_name_plural = 'Complaint Investigations'

    def __str__(self):
        return f"{self.complaint.complaint_id} - Investigation"
