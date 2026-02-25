from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import json
from datetime import datetime

from core.models import AuditedModel
from users.models import Department


class CAPA(AuditedModel):
    """
    Comprehensive Corrective And Preventive Actions (CAPA) model.
    Extends AuditedModel for full audit trail (created_by, created_at, updated_by, updated_at, is_active).
    Supports 140+ fields across identification, source, classification, phase tracking, 5W analysis,
    root cause analysis, risk matrix, planning, implementation, effectiveness, extensions, and closure.
    """

    # ============================================================================
    # SOURCE CHOICES & LINKS
    # ============================================================================
    SOURCE_CHOICES = (
        ('complaint', 'Complaint'),
        ('audit', 'Audit'),
        ('deviation', 'Deviation'),
        ('inspection', 'Inspection'),
        ('management_review', 'Management Review'),
        ('customer_feedback', 'Customer Feedback'),
        ('internal_observation', 'Internal Observation'),
        ('regulatory', 'Regulatory'),
        ('supplier', 'Supplier'),
    )

    CATEGORY_CHOICES = (
        ('product', 'Product'),
        ('process', 'Process'),
        ('system', 'System'),
        ('documentation', 'Documentation'),
        ('training', 'Training'),
        ('equipment', 'Equipment'),
        ('supplier', 'Supplier'),
        ('regulatory', 'Regulatory'),
    )

    PRIORITY_CHOICES = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    CAPA_TYPE_CHOICES = (
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
        ('both', 'Both Corrective & Preventive'),
    )

    PHASE_CHOICES = (
        ('investigation', 'Investigation'),
        ('root_cause', 'Root Cause Analysis'),
        ('risk_affirmation', 'Risk Affirmation'),
        ('capa_plan', 'CAPA Plan'),
        ('implementation', 'Implementation'),
        ('effectiveness', 'Effectiveness Verification'),
        ('closure', 'Closure'),
    )

    ROOT_CAUSE_METHOD_CHOICES = (
        ('five_why', '5 Why Analysis'),
        ('fishbone', 'Fishbone Diagram'),
        ('fmea', 'FMEA'),
        ('fault_tree', 'Fault Tree Analysis'),
        ('pareto', 'Pareto Analysis'),
        ('eight_d', '8D Problem Solving'),
        ('other', 'Other'),
    )

    RISK_ACCEPTABILITY_CHOICES = (
        ('acceptable', 'Acceptable'),
        ('tolerable', 'Tolerable'),
        ('unacceptable', 'Unacceptable'),
    )

    EFFECTIVENESS_RESULT_CHOICES = (
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('not_effective', 'Not Effective'),
        ('pending', 'Pending'),
    )

    EXTENSION_APPROVAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    # ============================================================================
    # IDENTIFICATION FIELDS
    # ============================================================================
    capa_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Auto-generated format: CAPA-YYYY-NNNN"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # ============================================================================
    # SOURCE & LINKS
    # ============================================================================
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    source_reference = models.TextField(
        blank=True,
        help_text="Reference number or description of the source"
    )
    complaint = models.ForeignKey(
        'complaints.Complaint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capas'
    )
    audit_finding = models.ForeignKey(
        'audit_mgmt.AuditFinding',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capas'
    )
    deviation = models.ForeignKey(
        'deviations.Deviation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capas'
    )

    # ============================================================================
    # CLASSIFICATION
    # ============================================================================
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    capa_type = models.CharField(
        max_length=20,
        choices=CAPA_TYPE_CHOICES,
        default='both'
    )

    # ============================================================================
    # PHASE TRACKING
    # ============================================================================
    current_phase = models.CharField(
        max_length=50,
        choices=PHASE_CHOICES,
        default='investigation'
    )
    phase_entered_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when entering current phase"
    )

    # ============================================================================
    # 5W ANALYSIS (5 Why)
    # ============================================================================
    what_happened = models.TextField(
        blank=True,
        help_text="What problem occurred?"
    )
    when_happened = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When did the problem occur?"
    )
    where_happened = models.TextField(
        blank=True,
        help_text="Where did the problem occur?"
    )
    who_affected = models.TextField(
        blank=True,
        help_text="Who was affected by the problem?"
    )
    why_happened = models.TextField(
        blank=True,
        help_text="Why did the problem happen?"
    )
    how_discovered = models.TextField(
        blank=True,
        help_text="How was the problem discovered?"
    )

    # ============================================================================
    # ROOT CAUSE ANALYSIS
    # ============================================================================
    root_cause_analysis_method = models.CharField(
        max_length=50,
        choices=ROOT_CAUSE_METHOD_CHOICES,
        blank=True
    )
    root_cause = models.TextField(
        blank=True,
        help_text="Identified root cause"
    )
    contributing_factors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of contributing factors"
    )
    root_cause_verified = models.BooleanField(
        default=False,
        help_text="Has root cause been verified?"
    )
    root_cause_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_root_cause_verifications'
    )
    root_cause_verified_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # ============================================================================
    # RISK MATRIX (RPN: Risk Priority Number = Severity × Occurrence × Detection)
    # ============================================================================
    risk_severity = models.IntegerField(
        default=1,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Severity: 1 (low) to 5 (high)"
    )
    risk_occurrence = models.IntegerField(
        default=1,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Occurrence: 1 (low) to 5 (high)"
    )
    risk_detection = models.IntegerField(
        default=1,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Detection: 1 (low) to 5 (high)"
    )
    risk_acceptability = models.CharField(
        max_length=20,
        choices=RISK_ACCEPTABILITY_CHOICES,
        default='tolerable'
    )
    pre_action_rpn = models.IntegerField(
        null=True,
        blank=True,
        help_text="Risk Priority Number before action (auto-computed)"
    )
    post_action_rpn = models.IntegerField(
        null=True,
        blank=True,
        help_text="Risk Priority Number after action (auto-computed)"
    )

    # ============================================================================
    # PLANNING & ACTIONS
    # ============================================================================
    planned_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Planned actions with descriptions, owners, and dates"
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_responsible_for'
    )
    target_completion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date for CAPA completion"
    )
    actual_completion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date of CAPA completion"
    )

    # ============================================================================
    # IMPLEMENTATION
    # ============================================================================
    implementation_notes = models.TextField(
        blank=True,
        help_text="Notes on implementation progress"
    )
    implementation_evidence = models.TextField(
        blank=True,
        help_text="Evidence of implementation (documents, records, etc.)"
    )
    implementation_verified = models.BooleanField(
        default=False,
        help_text="Has implementation been verified?"
    )
    implementation_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_implementation_verifications'
    )

    # ============================================================================
    # EFFECTIVENESS VERIFICATION
    # ============================================================================
    effectiveness_criteria = models.TextField(
        blank=True,
        help_text="Criteria to verify effectiveness"
    )
    effectiveness_check_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when effectiveness was checked"
    )
    effectiveness_result = models.CharField(
        max_length=50,
        choices=EFFECTIVENESS_RESULT_CHOICES,
        default='pending'
    )
    effectiveness_evidence = models.TextField(
        blank=True,
        help_text="Evidence of effectiveness"
    )
    effectiveness_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_effectiveness_verifications'
    )

    # ============================================================================
    # EXTENSION MANAGEMENT
    # ============================================================================
    has_extension = models.BooleanField(
        default=False,
        help_text="Has an extension been requested?"
    )
    extension_requested_date = models.DateTimeField(
        null=True,
        blank=True
    )
    extension_reason = models.TextField(
        blank=True,
        help_text="Reason for extension request"
    )
    extension_new_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="New target completion date after extension"
    )
    extension_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_extensions_approved'
    )
    extension_approval_status = models.CharField(
        max_length=20,
        choices=EXTENSION_APPROVAL_STATUS_CHOICES,
        default='pending'
    )

    # ============================================================================
    # CLOSURE
    # ============================================================================
    closure_comments = models.TextField(
        blank=True,
        help_text="Comments on CAPA closure"
    )
    closed_date = models.DateTimeField(
        null=True,
        blank=True
    )
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_closures'
    )

    # ============================================================================
    # DEPARTMENT & ASSIGNMENT
    # ============================================================================
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capas'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_assigned_to'
    )
    coordinator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_coordinated'
    )

    # ============================================================================
    # FLAGS & METRICS
    # ============================================================================
    is_recurring = models.BooleanField(
        default=False,
        help_text="Is this a recurring issue?"
    )
    recurrence_count = models.IntegerField(
        default=0,
        help_text="Number of times this issue has recurred"
    )
    requires_management_review = models.BooleanField(
        default=False,
        help_text="Does this CAPA require management review?"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'CAPA'
        verbose_name_plural = 'CAPAs'
        indexes = [
            models.Index(fields=['capa_id']),
            models.Index(fields=['current_phase']),
            models.Index(fields=['priority']),
            models.Index(fields=['source']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.capa_id} - {self.title}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate capa_id, compute RPN values."""
        # Auto-generate capa_id if not set
        if not self.capa_id:
            from django.utils import timezone as tz
            year = tz.now().year
            last = CAPA.objects.filter(capa_id__startswith=f'CAPA-{year}-').order_by('-capa_id').first()
            if last and last.capa_id:
                try:
                    seq = int(last.capa_id.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.capa_id = f'CAPA-{year}-{seq:04d}'

        # Auto-compute pre_action_rpn if not already set
        if self.pre_action_rpn is None:
            self.pre_action_rpn = self._calculate_rpn(
                self.risk_severity, self.risk_occurrence, self.risk_detection
            )

        # Update phase_entered_at if phase changed (check previous value)
        if self.pk:
            old_instance = CAPA.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.current_phase != self.current_phase:
                self.phase_entered_at = timezone.now()

        super().save(*args, **kwargs)

    @staticmethod
    def _calculate_rpn(severity, occurrence, detection):
        """Calculate Risk Priority Number = Severity × Occurrence × Detection."""
        return severity * occurrence * detection

    @property
    def risk_priority_number(self):
        """Calculate current RPN based on current risk parameters."""
        return self._calculate_rpn(
            self.risk_severity, self.risk_occurrence, self.risk_detection
        )

    def transition_to(self, new_phase, user=None):
        """
        Validate and transition to new phase.
        
        Args:
            new_phase: Target phase to transition to
            user: User performing the transition
            
        Raises:
            ValidationError: If transition is not valid
        """
        valid_transitions = {
            'investigation': ['root_cause'],
            'root_cause': ['risk_affirmation'],
            'risk_affirmation': ['capa_plan'],
            'capa_plan': ['implementation'],
            'implementation': ['effectiveness'],
            'effectiveness': ['closure'],
            'closure': [],
        }

        if new_phase not in valid_transitions.get(self.current_phase, []):
            raise ValidationError(
                f"Cannot transition from '{self.current_phase}' to '{new_phase}'"
            )

        self.current_phase = new_phase
        self.phase_entered_at = timezone.now()
        if user:
            self.updated_by = user

        self.save()

    def close_capa(self, user, comments=""):
        """Close the CAPA if effectiveness is confirmed."""
        if self.effectiveness_result not in ['effective', 'partially_effective']:
            raise ValidationError(
                f"Cannot close CAPA with effectiveness result: {self.effectiveness_result}"
            )

        self.current_phase = 'closure'
        self.closed_date = timezone.now()
        self.closed_by = user
        self.closure_comments = comments
        self.updated_by = user
        self.save()


class CAPAApproval(AuditedModel):
    """
    Multi-tier approval model for CAPA phases.
    Tracks approvals from coordinator, manager, QA head, review board, and regulatory.
    """

    PHASE_CHOICES = (
        ('investigation', 'Investigation'),
        ('root_cause', 'Root Cause Analysis'),
        ('risk_affirmation', 'Risk Affirmation'),
        ('capa_plan', 'CAPA Plan'),
        ('implementation', 'Implementation'),
        ('effectiveness', 'Effectiveness Verification'),
        ('closure', 'Closure'),
    )

    APPROVAL_TIER_CHOICES = (
        ('coordinator', 'CAPA Coordinator'),
        ('manager', 'Department Manager'),
        ('qa_head', 'QA Head'),
        ('review_board', 'Review Board'),
        ('regulatory', 'Regulatory'),
    )

    APPROVAL_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    )

    capa = models.ForeignKey(
        CAPA,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    phase = models.CharField(
        max_length=50,
        choices=PHASE_CHOICES
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='capa_approvals'
    )
    approval_tier = models.CharField(
        max_length=20,
        choices=APPROVAL_TIER_CHOICES
    )
    sequence = models.IntegerField(
        help_text="Approval sequence number (lower = earlier)"
    )
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    comments = models.TextField(blank=True)
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the approver responded"
    )
    signature = models.ForeignKey(
        'core.ElectronicSignature',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capa_approvals'
    )

    class Meta:
        unique_together = ('capa', 'phase', 'approver')
        ordering = ['approval_tier', 'sequence']
        verbose_name = 'CAPA Approval'
        verbose_name_plural = 'CAPA Approvals'

    def __str__(self):
        return f"{self.capa.capa_id} - {self.phase} - {self.approval_tier}"

    def approve(self, user, comments=""):
        """Record approval."""
        self.status = 'approved'
        self.approver = user
        self.responded_at = timezone.now()
        self.comments = comments
        self.updated_by = user
        self.save()

    def reject(self, user, comments=""):
        """Record rejection."""
        self.status = 'rejected'
        self.approver = user
        self.responded_at = timezone.now()
        self.comments = comments
        self.updated_by = user
        self.save()

    def defer(self, user, comments=""):
        """Defer approval decision."""
        self.status = 'deferred'
        self.approver = user
        self.responded_at = timezone.now()
        self.comments = comments
        self.updated_by = user
        self.save()


class CAPADocument(models.Model):
    """
    Supporting documents for CAPA organized by phase.
    Tracks document type, file, hash, and metadata.
    """

    PHASE_CHOICES = (
        ('investigation', 'Investigation'),
        ('root_cause', 'Root Cause Analysis'),
        ('risk_affirmation', 'Risk Affirmation'),
        ('capa_plan', 'CAPA Plan'),
        ('implementation', 'Implementation'),
        ('effectiveness', 'Effectiveness Verification'),
        ('closure', 'Closure'),
    )

    DOCUMENT_TYPE_CHOICES = (
        ('investigation_report', 'Investigation Report'),
        ('root_cause_analysis', 'Root Cause Analysis'),
        ('risk_assessment', 'Risk Assessment'),
        ('action_plan', 'Action Plan'),
        ('effectiveness_report', 'Effectiveness Report'),
        ('other', 'Other'),
    )

    capa = models.ForeignKey(
        CAPA,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    phase = models.CharField(
        max_length=50,
        choices=PHASE_CHOICES
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='capa_documents/%Y/%m/%d/')
    file_hash = models.CharField(
        max_length=256,
        blank=True,
        help_text="SHA-256 hash of file for integrity verification"
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='capa_documents_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['phase', '-uploaded_at']
        verbose_name = 'CAPA Document'
        verbose_name_plural = 'CAPA Documents'

    def __str__(self):
        return f"{self.capa.capa_id} - {self.title}"


class CAPAComment(models.Model):
    """
    Threaded comments for CAPA with support for inline discussion.
    Allows comments at CAPA level or specific to phases.
    """

    PHASE_CHOICES = (
        ('investigation', 'Investigation'),
        ('root_cause', 'Root Cause Analysis'),
        ('risk_affirmation', 'Risk Affirmation'),
        ('capa_plan', 'CAPA Plan'),
        ('implementation', 'Implementation'),
        ('effectiveness', 'Effectiveness Verification'),
        ('closure', 'Closure'),
    )

    capa = models.ForeignKey(
        CAPA,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='capa_comments'
    )
    comment = models.TextField()
    phase = models.CharField(
        max_length=50,
        choices=PHASE_CHOICES,
        null=True,
        blank=True,
        help_text="Specific phase this comment relates to"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment for threading"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'CAPA Comment'
        verbose_name_plural = 'CAPA Comments'

    def __str__(self):
        return f"Comment on {self.capa.capa_id} by {self.author.username}"
