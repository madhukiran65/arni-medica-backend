from django.db import models
from django.contrib.auth.models import User
from core.models import AuditedModel
from users.models import Department


class Document(AuditedModel):
    """Model for managing documents like SOPs, Work Instructions, Forms, and Policies."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('SOP', 'Standard Operating Procedure'),
        ('WI', 'Work Instruction'),
        ('FORM', 'Form'),
        ('POLICY', 'Policy'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('effective', 'Effective'),
        ('obsolete', 'Obsolete'),
    ]
    
    document_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique document identifier, e.g., 'AM-SOP-001'"
    )
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='documents')
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=50, default='1.0')
    revision_number = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    effective_date = models.DateTimeField(blank=True, null=True)
    next_review_date = models.DateTimeField(blank=True, null=True)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    file_hash = models.CharField(max_length=255, blank=True, null=True, help_text="SHA-256 hash of file")
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_documents')
    requires_approval = models.BooleanField(default=True)
    ai_classification = models.CharField(max_length=100, blank=True, null=True)
    ai_confidence = models.FloatField(default=0.0, help_text="AI classification confidence (0-1)")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_id']),
            models.Index(fields=['status']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.document_id} - {self.title}"


class DocumentVersion(models.Model):
    """Model for tracking document version history."""
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/versions/%Y/%m/%d/')
    file_hash = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('document', 'version_number')
    
    def __str__(self):
        return f"{self.document.document_id} - v{self.version_number}"


class DocumentChangeOrder(AuditedModel):
    """Model for managing document change orders."""
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
        ('closed', 'Closed'),
    ]
    
    CHANGE_TYPE_CHOICES = [
        ('major', 'Major Change'),
        ('minor', 'Minor Change'),
        ('editorial', 'Editorial Change'),
        ('urgent', 'Urgent Change'),
    ]
    
    dco_number = models.CharField(max_length=50, unique=True, help_text="Document Change Order number")
    title = models.CharField(max_length=255)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    affected_documents = models.ManyToManyField(Document, related_name='change_orders')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    estimated_review_days = models.IntegerField(default=7)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.dco_number} - {self.title}"


class DocumentChangeApproval(AuditedModel):
    """Model for tracking document change approvals."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    dco = models.ForeignKey(DocumentChangeOrder, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    signature_hash = models.CharField(max_length=255, blank=True, null=True, help_text="Hash of digital signature")
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('dco', 'approver')
    
    def __str__(self):
        return f"{self.dco.dco_number} - {self.approver.username}"
