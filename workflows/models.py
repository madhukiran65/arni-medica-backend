"""
Reusable Workflow Engine for Arni Medica AI-EQMS.
Every module (Documents, CAPA, Deviations, Complaints, Change Controls)
uses this engine for stage-based workflows with approval gates.

21 CFR Part 11 compliant: immutable approvals, electronic signatures,
audit trail integration.
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class WorkflowDefinition(models.Model):
    """
    Configurable workflow template for different record types.
    Each module (document, capa, deviation, etc.) has one or more workflow definitions.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    model_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Module this workflow applies to: document, capa, deviation, complaint, change_control"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'model_type')
        ordering = ['model_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.model_type})"

    @property
    def stage_count(self):
        return self.stages.count()


class WorkflowStage(models.Model):
    """
    Individual stage in a workflow (e.g., 'Draft', 'InReview', 'Approved').
    Stages define validation gates, required fields, and approval requirements.
    """
    workflow = models.ForeignKey(
        WorkflowDefinition, on_delete=models.CASCADE, related_name='stages'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    sequence = models.IntegerField(
        help_text="Order of this stage in the workflow (1, 2, 3...)"
    )
    description = models.TextField(blank=True)

    # Visual
    color = models.CharField(
        max_length=20, default='#6B7280',
        help_text="Hex color for UI display"
    )
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name for UI")

    # Validation gates
    required_fields = models.JSONField(
        default=list, blank=True,
        help_text="Fields that must be non-empty before entering this stage"
    )
    required_attachments = models.BooleanField(
        default=False,
        help_text="Whether at least one attachment is required"
    )

    # Approval requirements
    requires_approval = models.BooleanField(default=False)
    required_approvers_count = models.IntegerField(
        default=0,
        help_text="Minimum number of approvals needed to pass this stage"
    )

    # Signature requirements (21 CFR Part 11)
    requires_signature = models.BooleanField(default=False)
    signature_reason = models.CharField(
        max_length=100, blank=True,
        help_text="Reason code for electronic signature (e.g., 'approval', 'review')"
    )

    # Stage behavior
    is_initial = models.BooleanField(
        default=False,
        help_text="Is this the starting stage for new records?"
    )
    is_terminal = models.BooleanField(
        default=False,
        help_text="Is this a final stage (no outgoing transitions)?"
    )
    allows_edit = models.BooleanField(
        default=True,
        help_text="Can the record be edited while in this stage?"
    )
    auto_advance = models.BooleanField(
        default=False,
        help_text="Auto-advance to next stage when all approvals are met"
    )

    # SLA
    sla_days = models.IntegerField(
        null=True, blank=True,
        help_text="Expected days to complete this stage (for SLA tracking)"
    )

    class Meta:
        unique_together = ('workflow', 'sequence')
        ordering = ['workflow', 'sequence']

    def __str__(self):
        return f"{self.workflow.name} → {self.name} (#{self.sequence})"


class WorkflowTransition(models.Model):
    """
    Legal state transitions between stages.
    Only explicitly defined transitions are allowed — prevents invalid flows.
    """
    workflow = models.ForeignKey(
        WorkflowDefinition, on_delete=models.CASCADE, related_name='transitions'
    )
    from_stage = models.ForeignKey(
        WorkflowStage, on_delete=models.CASCADE, related_name='outgoing_transitions'
    )
    to_stage = models.ForeignKey(
        WorkflowStage, on_delete=models.CASCADE, related_name='incoming_transitions'
    )

    # UI display
    label = models.CharField(
        max_length=100, blank=True,
        help_text="Action label shown in UI (e.g., 'Submit for Review', 'Approve')"
    )
    description = models.TextField(blank=True)
    button_color = models.CharField(max_length=20, default='#3B82F6')

    # Permission gates
    required_permission = models.CharField(
        max_length=100, blank=True,
        help_text="Django permission codename required for this transition"
    )
    required_roles = models.JSONField(
        default=list, blank=True,
        help_text="List of role names that can execute this transition"
    )

    # Transition metadata
    estimated_duration_days = models.IntegerField(
        null=True, blank=True,
        help_text="Estimated days for this transition"
    )
    requires_comment = models.BooleanField(
        default=False,
        help_text="Require a comment/reason when executing this transition"
    )
    is_rejection = models.BooleanField(
        default=False,
        help_text="Is this a rejection/send-back transition?"
    )

    class Meta:
        unique_together = ('from_stage', 'to_stage')
        ordering = ['workflow', 'from_stage__sequence']

    def __str__(self):
        return f"{self.from_stage.name} → {self.to_stage.name} ({self.label})"


class WorkflowRecord(models.Model):
    """
    Binds a workflow state to an actual EQMS record.
    Uses GenericForeignKey so any model can have a workflow.
    """
    workflow = models.ForeignKey(
        WorkflowDefinition, on_delete=models.CASCADE, related_name='records'
    )
    current_stage = models.ForeignKey(
        WorkflowStage, on_delete=models.PROTECT, related_name='current_records'
    )

    # Generic FK to any EQMS record (Document, CAPA, Deviation, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    entered_stage_at = models.DateTimeField(default=timezone.now)
    estimated_exit_date = models.DateTimeField(
        null=True, blank=True,
        help_text="SLA deadline for current stage"
    )

    # Tracking
    stage_entry_count = models.IntegerField(
        default=1,
        help_text="How many times we've been in the current stage (for reopen tracking)"
    )
    is_active = models.BooleanField(default=True)
    is_overdue = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['current_stage', 'is_active']),
            models.Index(fields=['is_overdue']),
        ]
        ordering = ['-entered_stage_at']

    def __str__(self):
        return f"{self.content_object} @ {self.current_stage.name}"

    def check_overdue(self):
        """Check if the current stage has exceeded its SLA."""
        if self.estimated_exit_date and timezone.now() > self.estimated_exit_date:
            self.is_overdue = True
            self.save(update_fields=['is_overdue'])
        return self.is_overdue


class WorkflowHistory(models.Model):
    """
    Immutable history of all workflow transitions.
    Provides complete audit trail of stage changes.
    """
    workflow_record = models.ForeignKey(
        WorkflowRecord, on_delete=models.CASCADE, related_name='history'
    )
    from_stage = models.ForeignKey(
        WorkflowStage, on_delete=models.PROTECT, related_name='+'
    )
    to_stage = models.ForeignKey(
        WorkflowStage, on_delete=models.PROTECT, related_name='+'
    )
    transition = models.ForeignKey(
        WorkflowTransition, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Who and when
    transitioned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    transitioned_at = models.DateTimeField(default=timezone.now)

    # Context
    comments = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Duration tracking
    time_in_stage_seconds = models.BigIntegerField(
        null=True, blank=True,
        help_text="How long the record was in from_stage"
    )

    # Electronic signature reference
    signature = models.ForeignKey(
        'core.ElectronicSignature',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workflow_transitions'
    )

    class Meta:
        ordering = ['-transitioned_at']

    def __str__(self):
        return f"{self.from_stage.name} → {self.to_stage.name} by {self.transitioned_by}"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Workflow history records are immutable.")
        super().save(*args, **kwargs)


class WorkflowApprovalGate(models.Model):
    """
    Define approval requirements at a specific stage.
    Example: Document sign-off needs 2 QA reviewers + 1 Manager.
    """
    APPROVAL_MODE_CHOICES = [
        ('all', 'All must approve'),
        ('any', 'Any one can approve'),
        ('majority', 'Majority must approve'),
        ('count', 'Specific count required'),
    ]

    stage = models.ForeignKey(
        WorkflowStage, on_delete=models.CASCADE, related_name='approval_gates'
    )
    name = models.CharField(max_length=100, help_text="Gate name, e.g., 'QA Review'")
    required_role = models.CharField(
        max_length=100,
        help_text="Role required to approve at this gate"
    )
    required_count = models.IntegerField(
        default=1,
        help_text="Number of approvals required"
    )
    approval_mode = models.CharField(
        max_length=20, choices=APPROVAL_MODE_CHOICES, default='all'
    )
    sequence = models.IntegerField(
        default=1,
        help_text="Order of this gate (sequential gates must complete in order)"
    )
    estimated_response_days = models.IntegerField(
        default=3,
        help_text="Expected days for approvers to respond"
    )

    class Meta:
        ordering = ['stage', 'sequence']

    def __str__(self):
        return f"{self.stage.name} Gate: {self.name} ({self.required_role})"


class WorkflowApprovalRequest(models.Model):
    """
    Request for a specific user to approve at a gate.
    Created when a record enters a stage with approval gates.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
        ('expired', 'Expired'),
    ]

    gate = models.ForeignKey(
        WorkflowApprovalGate, on_delete=models.CASCADE, related_name='requests'
    )
    workflow_record = models.ForeignKey(
        WorkflowRecord, on_delete=models.CASCADE, related_name='approval_requests'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='approval_requests'
    )

    # Response
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)

    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    # Electronic signature (21 CFR Part 11)
    signature = models.OneToOneField(
        'core.ElectronicSignature',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approval_request'
    )

    class Meta:
        unique_together = ('gate', 'workflow_record', 'approver')
        ordering = ['gate__sequence', 'requested_at']

    def __str__(self):
        return f"{self.approver} → {self.gate.name} ({self.status})"

    def respond(self, status, comments='', signature=None):
        """
        Record approval response. Once responded, cannot be changed.
        """
        if self.status != 'pending':
            raise ValueError(
                f"Cannot respond to a request that is already '{self.status}'."
            )
        self.status = status
        self.comments = comments
        self.responded_at = timezone.now()
        self.signature = signature
        self.save()


class WorkflowDelegation(models.Model):
    """
    Allow users to delegate their approval authority to another user.
    Useful for vacations, role changes, etc.
    """
    delegator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='delegations_given'
    )
    delegate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='delegations_received'
    )
    workflow = models.ForeignKey(
        WorkflowDefinition, on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="Specific workflow, or null for all workflows"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reason = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.delegator} → {self.delegate} ({self.start_date} to {self.end_date})"
