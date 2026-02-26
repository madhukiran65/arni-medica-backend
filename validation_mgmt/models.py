from django.db import models
from django.contrib.auth.models import User
from core.models import AuditedModel


class ValidationPlan(AuditedModel):
    """Master validation plan for CSV/CSA activities"""

    VALIDATION_APPROACH_CHOICES = (
        ('traditional_csv', 'Traditional CSV'),
        ('risk_based_csa', 'Risk-Based CSA'),
        ('hybrid', 'Hybrid'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_execution', 'In Execution'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    )

    plan_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    system_name = models.CharField(max_length=255)
    system_version = models.CharField(max_length=100)
    description = models.TextField()
    scope = models.TextField()
    risk_assessment_summary = models.TextField(blank=True, null=True)
    validation_approach = models.CharField(
        max_length=20,
        choices=VALIDATION_APPROACH_CHOICES,
        default='traditional_csv'
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='validation_plans_responsible'
    )
    qa_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vp_qa_reviewed'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    target_completion = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        'users.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Validation Plan'
        verbose_name_plural = 'Validation Plans'

    def save(self, *args, **kwargs):
        if not self.plan_id:
            last_plan = ValidationPlan.objects.all().order_by('id').last()
            next_number = (last_plan.id + 1) if last_plan else 1
            self.plan_id = f'VP-{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plan_id}: {self.title}"


class ValidationProtocol(AuditedModel):
    """Validation protocols (IQ, OQ, PQ, UAT, etc.)"""

    PROTOCOL_TYPE_CHOICES = (
        ('iq', 'Installation Qualification'),
        ('oq', 'Operational Qualification'),
        ('pq', 'Performance Qualification'),
        ('uat', 'User Acceptance Testing'),
        ('regression', 'Regression Testing'),
        ('security', 'Security Testing'),
    )

    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('pass_with_deviations', 'Pass with Deviations'),
        ('not_executed', 'Not Executed'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_execution', 'In Execution'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    protocol_id = models.CharField(max_length=50, unique=True, editable=False)
    plan = models.ForeignKey(
        ValidationPlan,
        on_delete=models.CASCADE,
        related_name='protocols'
    )
    title = models.CharField(max_length=255)
    protocol_type = models.CharField(
        max_length=20,
        choices=PROTOCOL_TYPE_CHOICES
    )
    description = models.TextField()
    prerequisites = models.JSONField(default=list)
    test_environment = models.CharField(max_length=255)
    test_cases_data = models.JSONField(default=list)
    total_test_cases = models.IntegerField(default=0)
    passed_test_cases = models.IntegerField(default=0)
    failed_test_cases = models.IntegerField(default=0)
    execution_date = models.DateField(null=True, blank=True)
    result = models.CharField(
        max_length=30,
        choices=RESULT_CHOICES,
        default='not_executed'
    )
    result_summary = models.TextField(blank=True, null=True)
    deviations_noted = models.TextField(blank=True, null=True)
    executed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocols_executed'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocols_reviewed'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocols_approved'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    protocol_file = models.FileField(
        upload_to='validation_protocols/',
        null=True,
        blank=True
    )
    result_file = models.FileField(
        upload_to='validation_results/',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Validation Protocol'
        verbose_name_plural = 'Validation Protocols'

    def save(self, *args, **kwargs):
        if not self.protocol_id:
            last_protocol = ValidationProtocol.objects.all().order_by('id').last()
            next_number = (last_protocol.id + 1) if last_protocol else 1
            self.protocol_id = f'VPROT-{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.protocol_id}: {self.title}"


class ValidationTestCase(AuditedModel):
    """Individual test cases within protocols"""

    TEST_TYPE_CHOICES = (
        ('functional', 'Functional'),
        ('negative', 'Negative'),
        ('boundary', 'Boundary'),
        ('security', 'Security'),
        ('performance', 'Performance'),
        ('usability', 'Usability'),
    )

    STATUS_CHOICES = (
        ('not_executed', 'Not Executed'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('blocked', 'Blocked'),
        ('deferred', 'Deferred'),
    )

    PRIORITY_CHOICES = (
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )

    test_case_id = models.CharField(max_length=50, unique=True, editable=False)
    protocol = models.ForeignKey(
        ValidationProtocol,
        on_delete=models.CASCADE,
        related_name='test_cases'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    test_type = models.CharField(
        max_length=20,
        choices=TEST_TYPE_CHOICES
    )
    preconditions = models.TextField(blank=True, null=True)
    test_steps = models.JSONField(default=list)
    expected_result = models.TextField()
    actual_result = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_executed'
    )
    executed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_cases_executed'
    )
    execution_date = models.DateTimeField(null=True, blank=True)
    evidence_file = models.FileField(
        upload_to='validation_evidence/',
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Validation Test Case'
        verbose_name_plural = 'Validation Test Cases'

    def save(self, *args, **kwargs):
        if not self.test_case_id:
            last_test = ValidationTestCase.objects.all().order_by('id').last()
            next_number = (last_test.id + 1) if last_test else 1
            self.test_case_id = f'TC-{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test_case_id}: {self.title}"


class RTMEntry(AuditedModel):
    """Requirements Traceability Matrix entries"""

    REQUIREMENT_CATEGORY_CHOICES = (
        ('functional', 'Functional'),
        ('performance', 'Performance'),
        ('security', 'Security'),
        ('regulatory', 'Regulatory'),
        ('usability', 'Usability'),
        ('interface', 'Interface'),
    )

    VERIFICATION_STATUS_CHOICES = (
        ('not_verified', 'Not Verified'),
        ('verified', 'Verified'),
        ('partially_verified', 'Partially Verified'),
        ('failed', 'Failed'),
    )

    rtm_id = models.CharField(max_length=50, unique=True, editable=False)
    plan = models.ForeignKey(
        ValidationPlan,
        on_delete=models.CASCADE,
        related_name='rtm_entries'
    )
    requirement_id = models.CharField(max_length=100)
    requirement_text = models.TextField()
    requirement_source = models.CharField(max_length=255)
    requirement_category = models.CharField(
        max_length=20,
        choices=REQUIREMENT_CATEGORY_CHOICES
    )
    linked_test_cases = models.ManyToManyField(
        ValidationTestCase,
        blank=True,
        related_name='rtm_entries'
    )
    linked_protocol = models.ForeignKey(
        ValidationProtocol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rtm_entries'
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VERIFICATION_STATUS_CHOICES,
        default='not_verified'
    )
    gap_description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'RTM Entry'
        verbose_name_plural = 'RTM Entries'

    def save(self, *args, **kwargs):
        if not self.rtm_id:
            last_rtm = RTMEntry.objects.all().order_by('id').last()
            next_number = (last_rtm.id + 1) if last_rtm else 1
            self.rtm_id = f'RTM-{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rtm_id}: {self.requirement_id}"


class ValidationDeviation(AuditedModel):
    """Deviations found during validation"""

    SEVERITY_CHOICES = (
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('cosmetic', 'Cosmetic'),
    )

    RESOLUTION_TYPE_CHOICES = (
        ('fix_and_retest', 'Fix and Retest'),
        ('risk_accepted', 'Risk Accepted'),
        ('deferred', 'Deferred'),
        ('workaround', 'Workaround'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    deviation_id = models.CharField(max_length=50, unique=True, editable=False)
    protocol = models.ForeignKey(
        ValidationProtocol,
        on_delete=models.CASCADE,
        related_name='deviations'
    )
    test_case = models.ForeignKey(
        ValidationTestCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deviations'
    )
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )
    impact_assessment = models.TextField()
    resolution = models.TextField(blank=True, null=True)
    resolution_type = models.CharField(
        max_length=30,
        choices=RESOLUTION_TYPE_CHOICES,
        null=True,
        blank=True
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deviations_resolved'
    )
    resolution_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    linked_deviation = models.ForeignKey(
        'deviations.Deviation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validation_deviations'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Validation Deviation'
        verbose_name_plural = 'Validation Deviations'

    def save(self, *args, **kwargs):
        if not self.deviation_id:
            last_deviation = ValidationDeviation.objects.all().order_by('id').last()
            next_number = (last_deviation.id + 1) if last_deviation else 1
            self.deviation_id = f'VD-{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.deviation_id}: {self.description[:50]}"


class ValidationSummaryReport(AuditedModel):
    """Comprehensive validation summary report"""

    STATUS_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('not_applicable', 'Not Applicable'),
        ('not_executed', 'Not Executed'),
    )

    CONCLUSION_CHOICES = (
        ('validated', 'Validated'),
        ('not_validated', 'Not Validated'),
        ('conditionally_validated', 'Conditionally Validated'),
    )

    REPORT_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
    )

    report_id = models.CharField(max_length=50, unique=True, editable=False)
    plan = models.OneToOneField(
        ValidationPlan,
        on_delete=models.CASCADE,
        related_name='summary_report'
    )
    title = models.CharField(max_length=255)
    iq_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_executed'
    )
    oq_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_executed'
    )
    pq_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_executed'
    )
    overall_test_count = models.IntegerField(default=0)
    overall_pass_count = models.IntegerField(default=0)
    overall_fail_count = models.IntegerField(default=0)
    deviations_count = models.IntegerField(default=0)
    open_deviations_count = models.IntegerField(default=0)
    overall_conclusion = models.CharField(
        max_length=30,
        choices=CONCLUSION_CHOICES
    )
    executive_summary = models.TextField()
    recommendations = models.TextField()
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validation_reports_approved'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS_CHOICES,
        default='draft'
    )
    linked_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validation_reports'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Validation Summary Report'
        verbose_name_plural = 'Validation Summary Reports'

    def save(self, *args, **kwargs):
        if not self.report_id:
            last_report = ValidationSummaryReport.objects.all().order_by('id').last()
            next_number = (last_report.id + 1) if last_report else 1
            self.report_id = f'VSR-{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.report_id}: {self.title}"
