"""
Arni Medica AI-EQMS Document Control Module

This module provides a comprehensive document management system including:
- Document lifecycle management (draft, released, archived, obsolete)
- Version control with major/minor versioning
- Approval workflows and document checkout prevention
- Compliance tracking and regulatory requirements
- Change management and impact assessment
- AI-powered document classification
- Immutable snapshots at key lifecycle points
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
import hashlib
import json
from datetime import datetime, timedelta

from core.models import AuditedModel
from users.models import Department


class DocumentInfocardType(AuditedModel):
    """
    Document Type Classification with auto-generated prefixes.
    
    Defines the 26 standard document types used in pharmaceutical/medical device
    quality management systems, each with a unique 3-character prefix.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the document type (e.g., 'Standard Operating Procedure')"
    )
    prefix = models.CharField(
        max_length=3,
        unique=True,
        help_text="3-character unique prefix for auto-generated document IDs (e.g., 'SOP')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of this document type and its usage"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this document type is available for use"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = "Document Infocard Type"
        verbose_name_plural = "Document Infocard Types"
        indexes = [
            models.Index(fields=['prefix']),
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.prefix})"


class DocumentSubType(AuditedModel):
    """
    Document Subtype Classification dependent on parent Infocard Type.
    
    Allows further categorization of documents within a parent type.
    For example, SOP subtypes might include: Operational, Technical, Administrative.
    """
    
    infocard_type = models.ForeignKey(
        DocumentInfocardType,
        on_delete=models.CASCADE,
        related_name='subtypes',
        help_text="Parent document infocard type"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of this document subtype"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of this document subtype"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this subtype is available for use"
    )
    
    class Meta:
        ordering = ['infocard_type', 'name']
        verbose_name = "Document SubType"
        verbose_name_plural = "Document SubTypes"
        unique_together = [['infocard_type', 'name']]
        indexes = [
            models.Index(fields=['infocard_type', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.infocard_type.name} - {self.name}"


class DocumentCheckout(models.Model):
    """
    Prevent concurrent edits by tracking active checkouts.
    
    When a document is checked out for editing, it cannot be modified by other users.
    Only one active checkout per document is permitted.
    """
    
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        related_name='checkouts',
        help_text="Document being edited"
    )
    checked_out_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checked_out_documents',
        help_text="User who checked out the document"
    )
    checked_out_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when document was checked out"
    )
    checkout_reason = models.TextField(
        blank=True,
        help_text="Reason for checking out the document"
    )
    expected_checkin_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expected date when document will be checked back in"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this checkout is currently active"
    )
    
    class Meta:
        verbose_name = "Document Checkout"
        verbose_name_plural = "Document Checkouts"
        indexes = [
            models.Index(fields=['is_active', 'checked_out_by']),
            models.Index(fields=['document', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.document.document_id} - Checked out by {self.checked_out_by.username}"
    
    def is_document_checked_out(self):
        """Check if document is currently checked out."""
        return self.is_active


class DocumentApprover(models.Model):
    """
    Configurable approval chain for document approval workflows.
    
    Defines the sequence of approvers required to release a document,
    including their approval status and electronic signatures.
    """
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    ]
    
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        related_name='approvers',
        help_text="Document requiring approval"
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documents_to_approve',
        help_text="User responsible for approval"
    )
    sequence = models.PositiveIntegerField(
        help_text="Order in approval chain (lower number = earlier approval)"
    )
    role_required = models.CharField(
        max_length=100,
        blank=True,
        help_text="Required role/title for this approval step (e.g., 'QA Manager')"
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        help_text="Current approval status"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when approval was given"
    )
    comments = models.TextField(
        blank=True,
        help_text="Approver comments on the document"
    )
    signature = models.ForeignKey(
        'core.ElectronicSignature',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='document_approvals',
        help_text="Electronic signature for this approval"
    )
    is_final_approver = models.BooleanField(
        default=False,
        help_text="Whether this is the final approver in the chain"
    )

    class Meta:
        unique_together = [['document', 'approver']]
        ordering = ['sequence']
        verbose_name = "Document Approver"
        verbose_name_plural = "Document Approvers"
        indexes = [
            models.Index(fields=['document', 'sequence']),
            models.Index(fields=['approval_status']),
            models.Index(fields=['approver', 'approval_status']),
        ]
    
    def __str__(self):
        return f"{self.document.document_id} - {self.approver.username} (Step {self.sequence})"


class DocumentSnapshot(models.Model):
    """
    Immutable snapshot of document state at key lifecycle points.
    
    Captures the complete document state (including all fields and metadata)
    at critical moments: release, approval, archival, and review.
    Snapshots cannot be modified after creation, ensuring audit trail integrity.
    """
    
    SNAPSHOT_TYPE_CHOICES = [
        ('release', 'Release'),
        ('approval', 'Approval'),
        ('archive', 'Archive'),
        ('review', 'Review'),
        ('training_complete', 'Training Complete'),
        ('effective', 'Effective'),
        ('superseded', 'Superseded'),
        ('cancelled', 'Cancelled'),
    ]
    
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        related_name='snapshots',
        help_text="Document being snapshotted"
    )
    version_string = models.CharField(
        max_length=20,
        help_text="Version string at time of snapshot (e.g., '2.1')"
    )
    snapshot_type = models.CharField(
        max_length=20,
        choices=SNAPSHOT_TYPE_CHOICES,
        help_text="Type of lifecycle event triggering this snapshot"
    )
    snapshot_data = models.JSONField(
        help_text="Immutable frozen state of entire document at this point"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when snapshot was created"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_document_snapshots',
        help_text="User who created this snapshot"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document Snapshot"
        verbose_name_plural = "Document Snapshots"
        indexes = [
            models.Index(fields=['document', 'snapshot_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.document.document_id} v{self.version_string} - {self.snapshot_type}"
    
    def save(self, *args, **kwargs):
        """Override save to enforce immutability after creation."""
        if self.pk is not None:
            raise ValidationError("Document snapshots are immutable and cannot be modified.")
        super().save(*args, **kwargs)


class DocumentVersion(AuditedModel):
    """
    Enhanced version tracking with major/minor versioning and change tracking.
    
    Maintains complete history of document revisions including frozen snapshots
    of document content at each version point for audit trail purposes.
    """
    
    CHANGE_TYPE_CHOICES = [
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('editorial', 'Editorial'),
    ]
    
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        related_name='versions',
        help_text="Document this version belongs to"
    )
    major_version = models.PositiveIntegerField(
        help_text="Major version number (increments on significant changes)"
    )
    minor_version = models.PositiveIntegerField(
        default=0,
        help_text="Minor version number (increments on updates)"
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        default='minor',
        help_text="Type of change in this version"
    )
    is_major_change = models.BooleanField(
        default=False,
        help_text="Whether this is a major version change requiring all approvals"
    )
    change_summary = models.TextField(
        blank=True,
        help_text="Summary of changes in this version"
    )
    snapshot_data = models.JSONField(
        help_text="Frozen state of document at this version point"
    )
    released_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when this version was released"
    )
    
    class Meta:
        ordering = ['-major_version', '-minor_version']
        verbose_name = "Document Version"
        verbose_name_plural = "Document Versions"
        unique_together = [['document', 'major_version', 'minor_version']]
        indexes = [
            models.Index(fields=['document', 'major_version']),
            models.Index(fields=['released_date']),
            models.Index(fields=['change_type']),
        ]
    
    def __str__(self):
        return f"{self.document.document_id} v{self.major_version}.{self.minor_version}"


class DocumentChangeOrder(models.Model):
    """
    Enhanced change request tracking with impact assessment and regulatory tracking.
    
    Documents and tracks proposed changes to controlled documents,
    including impact analysis, regulatory implications, and training requirements.
    """
    
    CHANGE_STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
        ('closed', 'Closed'),
    ]
    
    document = models.ForeignKey(
        'Document',
        on_delete=models.CASCADE,
        related_name='change_orders',
        help_text="Document being changed"
    )
    change_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this change order"
    )
    title = models.CharField(
        max_length=255,
        help_text="Summary of the proposed change"
    )
    description = models.TextField(
        help_text="Detailed description of the change"
    )
    reason_for_change = models.TextField(
        help_text="Business or technical reason for this change"
    )
    proposed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proposed_changes',
        help_text="User who submitted this change request"
    )
    status = models.CharField(
        max_length=20,
        choices=CHANGE_STATUS_CHOICES,
        default='submitted',
        help_text="Current status of this change order"
    )
    impact_assessment = models.TextField(
        blank=True,
        help_text="Assessment of impacts from this change"
    )
    regulatory_impact = models.BooleanField(
        default=False,
        help_text="Whether this change impacts regulatory compliance"
    )
    training_impact = models.BooleanField(
        default=False,
        help_text="Whether this change requires employee training"
    )
    affected_processes = models.JSONField(
        default=list,
        help_text="List of processes/departments affected by this change"
    )
    implementation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Planned implementation date for this change"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when change order was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date when change order was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document Change Order"
        verbose_name_plural = "Document Change Orders"
        indexes = [
            models.Index(fields=['document', 'status']),
            models.Index(fields=['change_number']),
            models.Index(fields=['status']),
            models.Index(fields=['regulatory_impact']),
        ]
    
    def __str__(self):
        return f"{self.change_number} - {self.title}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate change_number."""
        if not self.change_number:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'DCO'
            last = DocumentChangeOrder.objects.filter(change_number__startswith=f'{prefix}-{year}-').order_by('-change_number').first()
            if last and getattr(last, 'change_number'):
                try:
                    seq = int(getattr(last, 'change_number').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.change_number = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


class DocumentChangeApproval(models.Model):
    """
    Approval tracking for document change orders.
    
    Records approvals and rejections in the change management workflow,
    including approver comments and timestamps.
    """
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    change_order = models.ForeignKey(
        DocumentChangeOrder,
        on_delete=models.CASCADE,
        related_name='approvals',
        help_text="Change order being approved"
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_approvals',
        help_text="User approving/rejecting this change"
    )
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        help_text="Approval decision"
    )
    comments = models.TextField(
        blank=True,
        help_text="Approver comments on the change"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of approval decision"
    )
    
    class Meta:
        ordering = ['-approved_at']
        verbose_name = "Document Change Approval"
        verbose_name_plural = "Document Change Approvals"
        indexes = [
            models.Index(fields=['change_order', 'status']),
            models.Index(fields=['approver']),
        ]
    
    def __str__(self):
        return f"{self.change_order.change_number} - {self.approver.username} ({self.status})"


class Document(AuditedModel):
    """
    Core Document Control module for pharmaceutical/medical device EQMS.
    
    Comprehensive 96+ field document management system supporting:
    - Document identification and organizational tracking
    - Advanced versioning (major.minor)
    - Lifecycle management (draft → released → archived → obsolete)
    - File management with SHA-256 hashing
    - Compliance and regulatory tracking
    - AI-powered document classification
    - Flexible custom fields via JSONField
    - Approval workflows and change management
    
    This is the cornerstone of the Arni Medica quality management system,
    ensuring all critical documents are properly controlled, versioned, and approved.
    """
    
    VAULT_STATE_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('training_period', 'Training Period'),
        ('effective', 'Effective'),
        ('superseded', 'Superseded'),
        ('obsolete', 'Obsolete'),
        ('archived', 'Archived'),
        ('cancelled', 'Cancelled'),
    ]
    
    DISTRIBUTION_RESTRICTION_CHOICES = [
        ('none', 'No Restriction'),
        ('internal', 'Internal Use Only'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted Distribution'),
    ]
    
    CONFIDENTIALITY_LEVEL_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('strictly_confidential', 'Strictly Confidential'),
    ]
    
    # --- IDENTIFICATION FIELDS ---
    document_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Auto-generated unique document identifier (e.g., 'SOP-2026-0001')"
    )
    legacy_document_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Legacy document ID from paper-based QMS (e.g., 'QA001-03')"
    )
    title = models.CharField(
        max_length=500,
        help_text="Official document title"
    )
    abbreviation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Short abbreviation or acronym for this document"
    )
    infocard_type = models.ForeignKey(
        DocumentInfocardType,
        on_delete=models.PROTECT,
        related_name='documents',
        help_text="Document classification type (SOP, Form, Work Instruction, etc.)"
    )
    subtype = models.ForeignKey(
        DocumentSubType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        help_text="Document subtype for further categorization"
    )
    
    # --- ORGANIZATIONAL FIELDS ---
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documents',
        help_text="Department responsible for this document"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_documents',
        help_text="Document owner responsible for maintenance and updates"
    )
    business_unit = models.CharField(
        max_length=100,
        blank=True,
        help_text="Business unit or function (e.g., 'Manufacturing', 'QA', 'R&D')"
    )
    site = models.CharField(
        max_length=100,
        blank=True,
        help_text="Physical site or location where document applies"
    )
    
    # --- VERSIONING FIELDS ---
    major_version = models.PositiveIntegerField(
        default=1,
        help_text="Major version number (significant changes)"
    )
    minor_version = models.PositiveIntegerField(
        default=0,
        help_text="Minor version number (incremental updates)"
    )
    revision_number = models.PositiveIntegerField(
        default=0,
        help_text="Revision number for draft changes"
    )
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_versions',
        help_text="Previous version of this document"
    )
    change_summary = models.TextField(
        blank=True,
        help_text="Summary of changes in current version"
    )
    
    # --- VAULT & LIFECYCLE FIELDS ---
    vault_state = models.CharField(
        max_length=20,
        choices=VAULT_STATE_CHOICES,
        default='draft',
        help_text="Current lifecycle state of document"
    )
    lifecycle_stage = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current stage in approval/release workflow"
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Whether document is locked from further edits"
    )
    locked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_documents',
        help_text="User who locked this document"
    )
    locked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when document was locked"
    )
    lock_reason = models.TextField(
        blank=True,
        help_text="Reason for document lock"
    )
    
    # --- DATE FIELDS ---
    effective_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when document becomes effective"
    )
    next_review_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled date for next document review"
    )
    last_reviewed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when document was last reviewed"
    )
    released_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when document was released to production"
    )
    obsolete_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when document became obsolete"
    )
    archived_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when document was archived"
    )
    review_period_months = models.PositiveIntegerField(
        default=24,
        help_text="Document review period in months (determines next_review_date)"
    )

    # --- ENHANCED LIFECYCLE FIELDS ---
    training_completion_required = models.BooleanField(
        default=False,
        help_text="Whether all training must be completed before document becomes effective"
    )
    training_completion_deadline_days = models.PositiveIntegerField(
        default=30,
        help_text="Number of days allowed for training completion after approval"
    )
    training_completed_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date when all required training was completed"
    )
    approved_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date when document was formally approved"
    )
    cancelled_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date when document was cancelled"
    )
    cancelled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cancelled_documents',
        help_text="User who cancelled this document"
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason for document cancellation"
    )
    superseded_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='supersedes_documents',
        help_text="Document that supersedes this one"
    )
    workflow_category = models.CharField(
        max_length=50, blank=True, default='standard',
        choices=[
            ('full_governance', 'Full Governance'),
            ('standard', 'Standard'),
            ('simplified', 'Simplified'),
            ('technical', 'Technical'),
            ('design_control', 'Design Control'),
            ('regulatory', 'Regulatory'),
            ('risk_management', 'Risk Management'),
            ('legal_contracts', 'Legal/Contracts'),
            ('training', 'Training'),
        ],
        help_text="Workflow category determining approval requirements"
    )

    # --- FILE FIELDS ---
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        null=True,
        blank=True,
        help_text="Primary document file"
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of uploaded file for integrity verification"
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Size of uploaded file in bytes"
    )
    file_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="MIME type of uploaded file (e.g., 'application/pdf')"
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original filename as uploaded"
    )
    external_file_url = models.URLField(
        blank=True,
        help_text="URL to external file if not stored locally"
    )
    
    # --- COMPLIANCE FIELDS ---
    regulatory_requirement = models.TextField(
        blank=True,
        help_text="Specific regulatory requirement(s) this document addresses"
    )
    requires_training = models.BooleanField(
        default=False,
        help_text="Whether employees require training on this document"
    )
    training_applicable_roles = models.JSONField(
        default=list,
        help_text="List of roles requiring training on this document"
    )
    distribution_restriction = models.CharField(
        max_length=20,
        choices=DISTRIBUTION_RESTRICTION_CHOICES,
        default='none',
        help_text="Distribution restriction level"
    )
    confidentiality_level = models.CharField(
        max_length=25,
        choices=CONFIDENTIALITY_LEVEL_CHOICES,
        default='internal',
        help_text="Data confidentiality classification"
    )
    subject_keywords = models.JSONField(
        default=list,
        help_text="Keywords for search and classification (e.g., ['sterilization', 'validation'])"
    )
    
    # --- AI FIELDS ---
    ai_classification = models.CharField(
        max_length=100,
        blank=True,
        help_text="AI-generated document classification"
    )
    ai_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score (0-1) for AI classification"
    )
    ai_classification_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when AI classification was performed"
    )
    
    # --- FLAG FIELDS ---
    requires_approval = models.BooleanField(
        default=True,
        help_text="Whether document requires formal approval before release"
    )
    is_template = models.BooleanField(
        default=False,
        help_text="Whether this document is a template for other documents"
    )
    is_controlled_copy = models.BooleanField(
        default=True,
        help_text="Whether this is a controlled master copy"
    )
    has_attachments = models.BooleanField(
        default=False,
        help_text="Whether document has related attachments"
    )
    watermark_text = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        default="Uncontrolled Copy if Printed",
        help_text="Watermark text for printed copies"
    )
    review_frequency_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Days between periodic reviews"
    )
    requires_dual_approval = models.BooleanField(
        default=False,
        help_text="Requires both Pharma QA and Device QA approval"
    )
    
    # --- DOCUMENT BODY / RICH TEXT CONTENT ---
    content = models.JSONField(
        default=dict, blank=True,
        help_text="TipTap/ProseMirror JSON document structure for in-browser editing"
    )
    content_html = models.TextField(
        blank=True, default='',
        help_text="Rendered HTML of the document content (auto-generated from content JSON)"
    )
    content_plain_text = models.TextField(
        blank=True, default='',
        help_text="Plain text extraction for full-text search"
    )
    description = models.TextField(
        blank=True, default='',
        help_text="Brief document description / abstract"
    )

    # --- FLEXIBLE CUSTOM FIELDS ---
    custom_fields = models.JSONField(
        default=dict,
        help_text="Flexible key-value pairs for client-specific requirements"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        indexes = [
            models.Index(fields=['document_id']),
            models.Index(fields=['vault_state']),
            models.Index(fields=['infocard_type', 'vault_state']),
            models.Index(fields=['department', 'vault_state']),
            models.Index(fields=['owner']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_locked']),
            models.Index(fields=['next_review_date']),
            models.Index(fields=['released_date']),
            models.Index(fields=['requires_approval']),
            models.Index(fields=['requires_training']),
            models.Index(fields=['is_template']),
            models.Index(fields=['major_version', 'minor_version']),
            models.Index(fields=['title']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.document_id} - {self.title} (v{self.version_string})"
    
    @property
    def version_string(self):
        """Return formatted version string like '2.1'."""
        return f"{self.major_version}.{self.minor_version}"
    
    def auto_generate_document_id(self):
        """
        Generate unique document ID using infocard type prefix with year and sequence.

        Uses the document's infocard_type prefix (e.g., SOP, FRM, WIS) to create
        IDs like 'SOP-2026-0001', 'FRM-2026-0012', etc.
        Falls back to 'DOC' if no infocard_type is set.

        Returns:
            str: Generated document ID like 'SOP-2026-0001'
        """
        from django.utils import timezone as tz
        year = tz.now().year

        # Use infocard type prefix if available, otherwise fallback to DOC
        if self.infocard_type_id:
            try:
                prefix = self.infocard_type.prefix
            except DocumentInfocardType.DoesNotExist:
                prefix = 'DOC'
        else:
            prefix = 'DOC'

        # Get the next sequence number for this prefix+year
        last_doc = Document.objects.filter(
            document_id__startswith=f'{prefix}-{year}-'
        ).order_by('-document_id').first()

        if last_doc:
            try:
                last_num = int(last_doc.document_id.split('-')[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1

        # Format with leading zeros (4-digit format: 0001, 0002, etc.)
        document_id = f"{prefix}-{year}-{next_num:04d}"

        # Ensure uniqueness
        qs = Document.objects.filter(document_id=document_id)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.exists():
            next_num += 1
            document_id = f"{prefix}-{year}-{next_num:04d}"
            qs = Document.objects.filter(document_id=document_id)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

        return document_id
    
    def calculate_file_hash(self):
        """
        Calculate SHA-256 hash of uploaded file.
        
        Returns:
            str: Hexadecimal SHA-256 hash of file content
        """
        if self.file:
            file_hash = hashlib.sha256()
            for chunk in self.file.chunks():
                file_hash.update(chunk)
            return file_hash.hexdigest()
        return ""
    
    def get_active_checkout(self):
        """Get the active checkout for this document, if any."""
        return self.checkouts.filter(is_active=True).first()

    def is_checkout_active(self):
        """Check if document has an active checkout."""
        return self.get_active_checkout() is not None

    def can_be_edited(self, user):
        """
        Determine if user can edit this document.

        Args:
            user (User): User attempting to edit

        Returns:
            bool: True if document can be edited by user
        """
        if self.is_locked:
            return self.locked_by == user

        active = self.get_active_checkout()
        if active:
            return active.checked_out_by == user

        return self.vault_state in ('draft', 'in_review')
    
    def get_approval_status(self):
        """
        Get summary of approval status from related DocumentApprover records.
        
        Returns:
            dict: Summary with pending, approved, rejected counts
        """
        approvers = self.approvers.all()
        return {
            'total': approvers.count(),
            'pending': approvers.filter(approval_status='pending').count(),
            'approved': approvers.filter(approval_status='approved').count(),
            'rejected': approvers.filter(approval_status='rejected').count(),
            'deferred': approvers.filter(approval_status='deferred').count(),
        }
    
    def is_fully_approved(self):
        """Check if all required approvers have approved."""
        if not self.requires_approval:
            return True
        
        approvers = self.approvers.all()
        if not approvers.exists():
            return False
        
        return not approvers.filter(
            approval_status__in=['pending', 'rejected', 'deferred']
        ).exists()
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate document ID and calculate file hash.
        """
        # Auto-generate document ID if not set
        if not self.document_id:
            self.document_id = self.auto_generate_document_id()
        
        # Calculate file hash if file is present
        if self.file and not self.file_hash:
            self.file_hash = self.calculate_file_hash()
            if self.file.size:
                self.file_size = self.file.size
        
        # Set original filename if not set
        if self.file and not self.original_filename:
            self.original_filename = self.file.name
        
        super().save(*args, **kwargs)


class DocumentComment(AuditedModel):
    """
    Inline comments on document content for review/correction workflows.

    Supports threaded replies, resolution tracking, and maps to specific
    text selections within the TipTap editor.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('wont_fix', "Won't Fix"),
    ]

    COMMENT_TYPE_CHOICES = [
        ('comment', 'Comment'),
        ('correction', 'Correction Required'),
        ('suggestion', 'Suggestion'),
        ('question', 'Question'),
    ]

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
        help_text="Parent comment (for threaded replies)"
    )
    author = models.ForeignKey(
        'auth.User', on_delete=models.PROTECT, related_name='document_comments'
    )

    # Content
    text = models.TextField(help_text="Comment text / correction note")
    comment_type = models.CharField(
        max_length=20, choices=COMMENT_TYPE_CHOICES, default='comment'
    )

    # Text selection reference (maps to TipTap marks)
    selection_from = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="ProseMirror position: start of highlighted text"
    )
    selection_to = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="ProseMirror position: end of highlighted text"
    )
    quoted_text = models.TextField(
        blank=True, default='',
        help_text="The text that was selected when the comment was made"
    )

    # Resolution
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    resolved_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Version tracking
    document_version = models.CharField(
        max_length=20, blank=True, default='',
        help_text="Document version when comment was created (e.g., '3.0')"
    )

    class Meta:
        ordering = ['selection_from', 'created_at']
        indexes = [
            models.Index(fields=['document', 'status']),
            models.Index(fields=['document', 'author']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        prefix = f"[{self.get_comment_type_display()}]"
        return f"{prefix} {self.author.username} on {self.document.document_id}: {self.text[:50]}"


class DocumentSuggestion(AuditedModel):
    """
    Track changes / suggestion mode for document corrections.

    When a reviewer edits text in suggestion mode, their changes are captured
    as suggestions (original_text → suggested_text) rather than applied directly.
    The document author can then accept or reject each suggestion.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    SUGGESTION_TYPE_CHOICES = [
        ('replace', 'Replace Text'),
        ('insert', 'Insert Text'),
        ('delete', 'Delete Text'),
        ('format', 'Format Change'),
    ]

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='suggestions'
    )
    author = models.ForeignKey(
        'auth.User', on_delete=models.PROTECT, related_name='document_suggestions'
    )

    # Suggestion type
    suggestion_type = models.CharField(
        max_length=20, choices=SUGGESTION_TYPE_CHOICES, default='replace'
    )

    # Text positions (ProseMirror positions)
    selection_from = models.PositiveIntegerField(
        help_text="ProseMirror position: start of affected text"
    )
    selection_to = models.PositiveIntegerField(
        help_text="ProseMirror position: end of affected text"
    )

    # Content
    original_text = models.TextField(
        blank=True, default='',
        help_text="Original text being replaced/deleted"
    )
    suggested_text = models.TextField(
        blank=True, default='',
        help_text="Suggested replacement text (empty for deletions)"
    )
    reason = models.TextField(
        blank=True, default='',
        help_text="Reason for the suggested change"
    )

    # Resolution
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )
    reviewed_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_suggestions'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Version tracking
    document_version = models.CharField(
        max_length=20, blank=True, default='',
        help_text="Document version when suggestion was created"
    )

    class Meta:
        ordering = ['selection_from', 'created_at']
        indexes = [
            models.Index(fields=['document', 'status']),
            models.Index(fields=['document', 'author']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        action = self.get_suggestion_type_display()
        return f"[{action}] {self.author.username} on {self.document.document_id}: {self.original_text[:30]}→{self.suggested_text[:30]}"


class DocumentAcknowledgment(AuditedModel):
    """
    Tracks user acknowledgment of documents.
    Records when users have read and understood critical documents.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='acknowledgments',
        help_text="Document being acknowledged"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doc_acknowledgments',
        help_text="User acknowledging the document"
    )
    acknowledged_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when document was acknowledged"
    )
    method = models.CharField(
        max_length=20,
        choices=(
            ('read', 'Read & Understood'),
            ('quiz', 'Completed Quiz'),
            ('signature', 'Electronic Signature')
        ),
        default='read',
        help_text="Method of acknowledgment"
    )

    class Meta:
        unique_together = ('document', 'user')
        ordering = ['-acknowledged_at']
        verbose_name = 'Document Acknowledgment'
        verbose_name_plural = 'Document Acknowledgments'
        indexes = [
            models.Index(fields=['document', 'user']),
            models.Index(fields=['acknowledged_at']),
        ]

    def __str__(self):
        return f"{self.user.username} acknowledged {self.document.document_id}"


# ElectronicSignature is defined in core.models — use core.ElectronicSignature
