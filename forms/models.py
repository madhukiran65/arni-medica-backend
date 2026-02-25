from django.db import models
from django.conf import settings
from core.models import AuditedModel
from users.models import Department


class FormTemplate(AuditedModel):
    """Form template for audit, investigation, deviation tracking, etc."""
    
    TEMPLATE_TYPE_CHOICES = [
        ('audit_checklist', 'Audit Checklist'),
        ('investigation_form', 'Investigation Form'),
        ('deviation_checklist', 'Deviation Checklist'),
        ('protocol', 'Protocol'),
        ('inspection_form', 'Inspection Form'),
        ('review_form', 'Review Form'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    version = models.CharField(max_length=50, default='1.0')
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_templates'
    )
    category = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Form Template'
        verbose_name_plural = 'Form Templates'
        indexes = [
            models.Index(fields=['template_type', 'is_published']),
            models.Index(fields=['department', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} (v{self.version})"


class FormSection(models.Model):
    """Section within a form template for organizing questions."""
    
    template = models.ForeignKey(
        FormTemplate,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sequence = models.IntegerField()
    is_repeatable = models.BooleanField(default=False)
    conditions = models.JSONField(blank=True, null=True, help_text='Conditional show/hide logic')
    
    class Meta:
        ordering = ['sequence']
        unique_together = [['template', 'sequence']]
        verbose_name = 'Form Section'
        verbose_name_plural = 'Form Sections'
        indexes = [
            models.Index(fields=['template', 'sequence']),
        ]
    
    def __str__(self):
        return f"{self.template.name} - {self.title}"


class FormQuestion(models.Model):
    """Individual question within a form section."""
    
    QUESTION_TYPE_CHOICES = [
        ('text', 'Short Text'),
        ('textarea', 'Long Text'),
        ('number', 'Number'),
        ('decimal', 'Decimal'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('time', 'Time'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('phone', 'Phone'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio Button'),
        ('dropdown', 'Dropdown'),
        ('multi_select', 'Multi-Select'),
        ('file_upload', 'File Upload'),
        ('image_upload', 'Image Upload'),
        ('signature', 'Signature'),
        ('rating', 'Rating'),
        ('scale', 'Scale'),
        ('matrix', 'Matrix'),
        ('formula', 'Formula'),
        ('conditional', 'Conditional'),
        ('yes_no', 'Yes/No'),
        ('pass_fail', 'Pass/Fail'),
    ]
    
    section = models.ForeignKey(
        FormSection,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    help_text = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    sequence = models.IntegerField()
    options = models.JSONField(
        blank=True,
        null=True,
        help_text='For radio/dropdown/multi_select: list of {value, label}'
    )
    validation_rules = models.JSONField(
        blank=True,
        null=True,
        help_text='Validation rules: min, max, regex, etc.'
    )
    default_value = models.CharField(max_length=255, blank=True)
    placeholder = models.CharField(max_length=255, blank=True)
    scoring_weight = models.IntegerField(default=0, help_text='Weight for scored forms')
    conditions = models.JSONField(blank=True, null=True, help_text='Conditional visibility logic')
    
    class Meta:
        ordering = ['sequence']
        verbose_name = 'Form Question'
        verbose_name_plural = 'Form Questions'
        indexes = [
            models.Index(fields=['section', 'sequence']),
            models.Index(fields=['question_type']),
        ]
    
    def __str__(self):
        return f"Q{self.sequence}: {self.question_text[:50]}"


class FormInstance(AuditedModel):
    """Completed form instance tied to a context (audit, deviation, etc)."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]
    
    template = models.ForeignKey(
        FormTemplate,
        on_delete=models.PROTECT,
        related_name='instances'
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='completed_forms'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    context_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='What this form is attached to (e.g., audit, deviation)'
    )
    context_id = models.CharField(max_length=100, blank=True)
    score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_possible_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Form Instance'
        verbose_name_plural = 'Form Instances'
        indexes = [
            models.Index(fields=['template', 'status']),
            models.Index(fields=['context_type', 'context_id']),
            models.Index(fields=['completed_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.template.name} - {self.get_status_display()}"


class FormResponse(models.Model):
    """Individual response/answer to a form question."""
    
    instance = models.ForeignKey(
        FormInstance,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        FormQuestion,
        on_delete=models.PROTECT,
        related_name='responses'
    )
    response_text = models.TextField(blank=True)
    response_number = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    response_boolean = models.BooleanField(null=True, blank=True)
    response_json = models.JSONField(blank=True, null=True, help_text='For complex responses: multi_select, matrix')
    response_file = models.FileField(upload_to='form_responses/%Y/%m/', null=True, blank=True)
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['instance', 'question']]
        verbose_name = 'Form Response'
        verbose_name_plural = 'Form Responses'
        indexes = [
            models.Index(fields=['instance', 'question']),
        ]
    
    def __str__(self):
        return f"Response to {self.question.question_text[:30]}"
