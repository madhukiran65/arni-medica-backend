from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from core.models import AuditedModel
from users.models import Department, ProductLine, Site

User = get_user_model()


class DesignProject(AuditedModel):
    PRODUCT_TYPE_CHOICES = (
        ('device', 'Medical Device'),
        ('ivd', 'In Vitro Diagnostic'),
        ('combination', 'Combination Product'),
        ('drug_device', 'Drug-Device Combination'),
    )

    CURRENT_PHASE_CHOICES = (
        ('planning', 'Planning'),
        ('design_input', 'Design Input'),
        ('design_output', 'Design Output'),
        ('verification', 'Verification'),
        ('validation', 'Validation'),
        ('transfer', 'Design Transfer'),
        ('production', 'Production'),
    )

    REGULATORY_PATHWAY_CHOICES = (
        ('510k', '510(k)'),
        ('pma', 'PMA'),
        ('de_novo', 'De Novo'),
        ('exempt', 'Exempt'),
        ('ce_mark', 'CE Mark'),
        ('ivdr', 'IVDR'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    project_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    current_phase = models.CharField(max_length=20, choices=CURRENT_PHASE_CHOICES, default='planning')
    project_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_projects')
    regulatory_pathway = models.CharField(max_length=20, choices=REGULATORY_PATHWAY_CHOICES)
    target_completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    product_line = models.ForeignKey(ProductLine, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_id']),
            models.Index(fields=['status']),
            models.Index(fields=['current_phase']),
        ]

    def __str__(self):
        return f"{self.project_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.project_id:
            last_project = DesignProject.objects.all().order_by('-created_at').first()
            if last_project and last_project.project_id:
                try:
                    last_num = int(last_project.project_id.split('-')[1])
                    self.project_id = f"DP-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.project_id = "DP-0001"
            else:
                self.project_id = "DP-0001"
        super().save(*args, **kwargs)


class UserNeed(AuditedModel):
    SOURCE_CHOICES = (
        ('clinical', 'Clinical'),
        ('marketing', 'Marketing'),
        ('regulatory', 'Regulatory'),
        ('engineering', 'Engineering'),
        ('manufacturing', 'Manufacturing'),
        ('customer_feedback', 'Customer Feedback'),
    )

    PRIORITY_CHOICES = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
    )

    need_id = models.CharField(max_length=20, unique=True, editable=False)
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='user_needs')
    description = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    acceptance_criteria = models.TextField(blank=True)
    rationale = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_user_needs')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['need_id']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.need_id} - {self.description[:50]}"

    def save(self, *args, **kwargs):
        if not self.need_id:
            last_need = UserNeed.objects.all().order_by('-created_at').first()
            if last_need and last_need.need_id:
                try:
                    last_num = int(last_need.need_id.split('-')[1])
                    self.need_id = f"UN-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.need_id = "UN-0001"
            else:
                self.need_id = "UN-0001"
        super().save(*args, **kwargs)


class DesignInput(AuditedModel):
    INPUT_TYPE_CHOICES = (
        ('functional', 'Functional'),
        ('performance', 'Performance'),
        ('safety', 'Safety'),
        ('regulatory', 'Regulatory'),
        ('environmental', 'Environmental'),
        ('interface', 'Interface'),
        ('packaging', 'Packaging'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
    )

    input_id = models.CharField(max_length=20, unique=True, editable=False)
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='design_inputs')
    specification = models.TextField()
    measurable_criteria = models.TextField()
    input_type = models.CharField(max_length=20, choices=INPUT_TYPE_CHOICES)
    tolerance = models.CharField(max_length=255, blank=True)
    test_method = models.TextField(blank=True)
    linked_user_needs = models.ManyToManyField(UserNeed, blank=True, related_name='linked_inputs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_design_inputs')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['input_id']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.input_id} - {self.specification[:50]}"

    def save(self, *args, **kwargs):
        if not self.input_id:
            last_input = DesignInput.objects.all().order_by('-created_at').first()
            if last_input and last_input.input_id:
                try:
                    last_num = int(last_input.input_id.split('-')[1])
                    self.input_id = f"DI-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.input_id = "DI-0001"
            else:
                self.input_id = "DI-0001"
        super().save(*args, **kwargs)


class DesignOutput(AuditedModel):
    OUTPUT_TYPE_CHOICES = (
        ('drawing', 'Drawing'),
        ('specification', 'Specification'),
        ('software', 'Software'),
        ('formula', 'Formula'),
        ('process', 'Process'),
        ('labeling', 'Labeling'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
    )

    output_id = models.CharField(max_length=20, unique=True, editable=False)
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='design_outputs')
    description = models.TextField()
    output_type = models.CharField(max_length=20, choices=OUTPUT_TYPE_CHOICES)
    file = models.FileField(upload_to='design_outputs/', null=True, blank=True)
    revision = models.CharField(max_length=50, blank=True, default='1.0')
    linked_inputs = models.ManyToManyField(DesignInput, blank=True, related_name='linked_outputs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_design_outputs')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['output_id']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.output_id} - {self.description[:50]}"

    def save(self, *args, **kwargs):
        if not self.output_id:
            last_output = DesignOutput.objects.all().order_by('-created_at').first()
            if last_output and last_output.output_id:
                try:
                    last_num = int(last_output.output_id.split('-')[1])
                    self.output_id = f"DO-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.output_id = "DO-0001"
            else:
                self.output_id = "DO-0001"
        super().save(*args, **kwargs)


class VVProtocol(AuditedModel):
    PROTOCOL_TYPE_CHOICES = (
        ('verification', 'Verification'),
        ('validation', 'Validation'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('executed', 'Executed'),
        ('failed', 'Failed'),
        ('superseded', 'Superseded'),
    )

    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional'),
        ('not_executed', 'Not Executed'),
    )

    protocol_id = models.CharField(max_length=20, unique=True, editable=False)
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='vv_protocols')
    title = models.CharField(max_length=255)
    protocol_type = models.CharField(max_length=20, choices=PROTOCOL_TYPE_CHOICES)
    test_method = models.TextField()
    acceptance_criteria = models.TextField()
    sample_size = models.IntegerField(null=True, blank=True)
    linked_inputs = models.ManyToManyField(DesignInput, blank=True, related_name='vv_protocols')
    linked_outputs = models.ManyToManyField(DesignOutput, blank=True, related_name='vv_protocols')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    execution_date = models.DateField(null=True, blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='not_executed')
    result_summary = models.TextField(blank=True)
    deviations_noted = models.TextField(blank=True)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='executed_vv_protocols')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_vv_protocols')
    file = models.FileField(upload_to='vv_protocols/', null=True, blank=True)
    result_file = models.FileField(upload_to='vv_results/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['protocol_id']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.protocol_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.protocol_id:
            last_protocol = VVProtocol.objects.all().order_by('-created_at').first()
            if last_protocol and last_protocol.protocol_id:
                try:
                    last_num = int(last_protocol.protocol_id.split('-')[1])
                    self.protocol_id = f"VV-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.protocol_id = "VV-0001"
            else:
                self.protocol_id = "VV-0001"
        super().save(*args, **kwargs)


class DesignReview(AuditedModel):
    PHASE_CHOICES = (
        ('planning', 'Planning'),
        ('design_input', 'Design Input'),
        ('design_output', 'Design Output'),
        ('verification', 'Verification'),
        ('validation', 'Validation'),
        ('transfer', 'Design Transfer'),
        ('production', 'Production'),
    )

    OUTCOME_CHOICES = (
        ('approved', 'Approved'),
        ('conditional', 'Conditional'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    )

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    review_id = models.CharField(max_length=20, unique=True, editable=False)
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='design_reviews')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES)
    review_date = models.DateField()
    attendees = models.ManyToManyField(User, blank=True, related_name='design_reviews_attended')
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    action_items = JSONField(default=list)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    conditions = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['review_id']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.review_id} - {self.project.title}"

    def save(self, *args, **kwargs):
        if not self.review_id:
            last_review = DesignReview.objects.all().order_by('-created_at').first()
            if last_review and last_review.review_id:
                try:
                    last_num = int(last_review.review_id.split('-')[1])
                    self.review_id = f"DR-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.review_id = "DR-0001"
            else:
                self.review_id = "DR-0001"
        super().save(*args, **kwargs)


class DesignTransfer(AuditedModel):
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    transfer_id = models.CharField(max_length=20, unique=True, editable=False)
    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='design_transfers')
    description = models.TextField()
    transfer_checklist = JSONField(default=list)
    manufacturing_site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    production_readiness_confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_design_transfers')
    confirmed_date = models.DateField(null=True, blank=True)
    linked_document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transfer_id']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.transfer_id} - {self.project.title}"

    def save(self, *args, **kwargs):
        if not self.transfer_id:
            last_transfer = DesignTransfer.objects.all().order_by('-created_at').first()
            if last_transfer and last_transfer.transfer_id:
                try:
                    last_num = int(last_transfer.transfer_id.split('-')[1])
                    self.transfer_id = f"DT-{last_num + 1:04d}"
                except (IndexError, ValueError):
                    self.transfer_id = "DT-0001"
            else:
                self.transfer_id = "DT-0001"
        super().save(*args, **kwargs)


class TraceabilityLink(AuditedModel):
    LINK_STATUS_CHOICES = (
        ('complete', 'Complete'),
        ('partial', 'Partial'),
        ('missing', 'Missing'),
    )

    project = models.ForeignKey(DesignProject, on_delete=models.CASCADE, related_name='traceability_links')
    user_need = models.ForeignKey(UserNeed, on_delete=models.CASCADE, null=True, blank=True)
    design_input = models.ForeignKey(DesignInput, on_delete=models.CASCADE, null=True, blank=True)
    design_output = models.ForeignKey(DesignOutput, on_delete=models.CASCADE, null=True, blank=True)
    vv_protocol = models.ForeignKey(VVProtocol, on_delete=models.CASCADE, null=True, blank=True)
    link_status = models.CharField(max_length=20, choices=LINK_STATUS_CHOICES, default='complete')
    gap_description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['link_status']),
        ]

    def __str__(self):
        items = []
        if self.user_need:
            items.append(str(self.user_need))
        if self.design_input:
            items.append(str(self.design_input))
        if self.design_output:
            items.append(str(self.design_output))
        if self.vv_protocol:
            items.append(str(self.vv_protocol))
        return f"TraceabilityLink: {' -> '.join(items)}"
