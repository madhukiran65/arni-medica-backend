"""
Core models for Arni Medica AI-EQMS
21 CFR Part 11 compliant audit trail and electronic signatures
"""
import hashlib
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class AuditedModel(models.Model):
    """
    Abstract base model providing 21 CFR Part 11 compliant audit trail.
    Every EQMS record (documents, CAPAs, complaints, etc.) inherits this.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_created', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_updated', null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Attachment(models.Model):
    """File attachment with SHA-256 integrity verification."""
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    file_size = models.BigIntegerField()
    file_hash = models.CharField(max_length=128, blank=True)  # SHA-256
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file_name

    def compute_hash(self):
        """Compute SHA-256 hash for file integrity verification."""
        sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            sha256.update(chunk)
        return sha256.hexdigest()

    def save(self, *args, **kwargs):
        if self.file and not self.file_hash:
            self.file_hash = self.compute_hash()
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """
    Immutable audit trail — 21 CFR Part 11 compliance.
    Records WHO changed WHAT, WHEN, and the before/after values.
    This model should NEVER be updated or deleted.
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('sign', 'Electronically Signed'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('transition', 'Status Transition'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
    ]

    # What was changed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, blank=True)

    # Who changed it
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    # When
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Where (client context)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # What changed (before/after values as JSON)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    change_summary = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
        ]
        # Prevent deletion at the Django level
        managed = True

    def __str__(self):
        return f"{self.action} {self.object_repr} by {self.user} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Prevent updates to existing audit logs (immutability)
        if self.pk:
            raise ValueError("Audit logs are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit logs are immutable and cannot be deleted.")


class ElectronicSignature(models.Model):
    """
    21 CFR Part 11 electronic signature record.
    Requires password re-entry — not just a button click.
    Cryptographically binds the user to the signed content.
    Supports signature invalidation for compliance with audit trail requirements.
    """
    SIGNATURE_MEANING_CHOICES = [
        ('approval', 'Approval'),
        ('rejection', 'Rejection'),
        ('review', 'Review'),
        ('acknowledgment', 'Acknowledgment'),
        ('verification', 'Verification'),
        ('authoring', 'Authoring'),
    ]

    REASON_CHOICES = [
        ('approval', 'Document Approval'),
        ('review', 'Document Review'),
        ('capa_closure', 'CAPA Closure'),
        ('complaint_closure', 'Complaint Closure'),
        ('audit_closure', 'Audit Closure'),
        ('training_completion', 'Training Completion'),
        ('change_approval', 'Change Order Approval'),
    ]

    # What was signed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Who signed
    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='electronic_signatures'
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Signature details
    signature_meaning = models.CharField(
        max_length=30, choices=SIGNATURE_MEANING_CHOICES, default='approval'
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, blank=True, null=True)
    meaning = models.TextField(help_text="What the signer is attesting to")

    # Cryptographic binding
    content_hash = models.CharField(max_length=128)  # SHA-256 of signed content
    signature_hash = models.CharField(max_length=128)  # SHA-256(user_id + content_hash + timestamp)

    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Signature validity tracking (21 CFR Part 11)
    is_valid = models.BooleanField(default=True, db_index=True)
    invalidated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='invalidated_signatures', null=True, blank=True
    )
    invalidated_at = models.DateTimeField(null=True, blank=True)
    invalidation_reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['signer', 'timestamp']),
            models.Index(fields=['is_valid']),
        ]

    def __str__(self):
        status = "Valid" if self.is_valid else "Invalidated"
        return f"{status} signature by {self.signer} on {self.timestamp}"

    def invalidate(self, user, reason):
        """Mark signature as invalid (immutable audit trail)."""
        if not self.is_valid:
            raise ValueError("Signature is already invalidated")
        self.is_valid = False
        self.invalidated_by = user
        self.invalidated_at = timezone.now()
        self.invalidation_reason = reason
        self.save(update_fields=['is_valid', 'invalidated_by', 'invalidated_at', 'invalidation_reason'])

    @staticmethod
    def create_signature(user, content_type, object_id, content_str, signature_meaning,
                        meaning, reason=None, ip_address=None):
        """Create a verified electronic signature."""
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        timestamp = timezone.now()
        sig_input = f"{user.id}|{content_hash}|{timestamp.isoformat()}"
        signature_hash = hashlib.sha256(sig_input.encode()).hexdigest()

        return ElectronicSignature.objects.create(
            content_type=content_type,
            object_id=str(object_id),
            signer=user,
            timestamp=timestamp,
            signature_meaning=signature_meaning,
            reason=reason,
            meaning=meaning,
            content_hash=content_hash,
            signature_hash=signature_hash,
            ip_address=ip_address,
        )
