from django.db import models
from django.conf import settings
from core.models import AuditedModel


class FeedbackTicket(AuditedModel):
    """User-submitted bug reports, improvement suggestions, and feedback."""

    TYPE_CHOICES = [
        ('bug_report', 'Bug Report'),
        ('improvement', 'Improvement Suggestion'),
        ('feedback', 'General Feedback'),
        ('question', 'Question'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('documents', 'Documents'),
        ('capa', 'CAPA'),
        ('complaints', 'Complaints & PMS'),
        ('deviations', 'Deviations'),
        ('training', 'Training'),
        ('change_controls', 'Change Controls'),
        ('suppliers', 'Suppliers'),
        ('audits', 'Audits'),
        ('workflows', 'Workflows'),
        ('forms', 'Forms'),
        ('risk_management', 'Risk Management'),
        ('design_controls', 'Design Controls'),
        ('equipment', 'Equipment'),
        ('batch_records', 'Batch Records'),
        ('validation', 'Validation'),
        ('management_review', 'Management Review'),
        ('admin_settings', 'Admin Settings'),
        ('general', 'General / Other'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    module = models.CharField(max_length=30, choices=MODULE_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='feedback_submitted'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='feedback_assigned'
    )

    resolution_summary = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ticket_id} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last = FeedbackTicket.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.ticket_id = f'FB-{next_num:04d}'
        super().save(*args, **kwargs)


class FeedbackAttachment(models.Model):
    """File attachments (screenshots, videos) for feedback tickets."""

    ticket = models.ForeignKey(
        FeedbackTicket, on_delete=models.CASCADE, related_name='attachments'
    )
    file = models.FileField(upload_to='feedback/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.BigIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='feedback_attachments'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file_name} ({self.ticket.ticket_id})'
