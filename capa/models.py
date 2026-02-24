from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class AuditedModel(models.Model):
    """Base model with audit trail"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True


class CAPA(AuditedModel):
    SOURCE_CHOICES = (
        ('complaint', 'Complaint'),
        ('internal_audit', 'Internal Audit'),
        ('incoming_inspection', 'Incoming Inspection'),
        ('management_review', 'Management Review'),
        ('process_monitoring', 'Process Monitoring'),
    )

    PRIORITY_CHOICES = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    STATUS_CHOICES = (
        ('investigation', 'Investigation'),
        ('root_cause_analysis', 'Root Cause Analysis'),
        ('action_planning', 'Action Planning'),
        ('effectiveness_verification', 'Effectiveness Verification'),
        ('closed', 'Closed'),
    )

    capa_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='capa_owned')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='investigation')
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    root_cause = models.TextField(blank=True)
    root_cause_analysis_method = models.CharField(max_length=100, blank=True)
    corrective_actions = models.TextField(blank=True)
    preventive_actions = models.TextField(blank=True)
    verification_method = models.CharField(max_length=100, blank=True)
    verification_results = models.TextField(blank=True)
    verification_date = models.DateField(null=True, blank=True)
    ai_root_cause = models.TextField(blank=True)
    ai_confidence = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'CAPA'
        verbose_name_plural = 'CAPAs'

    def __str__(self):
        return f"{self.capa_id} - {self.title}"

    def transition_to(self, new_status):
        """Validate and transition to new status"""
        valid_transitions = {
            'investigation': ['root_cause_analysis'],
            'root_cause_analysis': ['action_planning'],
            'action_planning': ['effectiveness_verification'],
            'effectiveness_verification': ['closed'],
            'closed': [],
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValidationError(f"Cannot transition from {self.status} to {new_status}")

        self.status = new_status
        self.save()


class CAPAAction(AuditedModel):
    ACTION_TYPE_CHOICES = (
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    )

    capa = models.ForeignKey(CAPA, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    description = models.TextField()
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='capa_actions')
    target_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.capa.capa_id} - {self.action_type.title()}"
