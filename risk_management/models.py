from django.db import models
from django.contrib.auth.models import User
from core.models import AuditedModel


class RiskCategory(AuditedModel):
    """Categories for classifying risks"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Risk Category'
        verbose_name_plural = 'Risk Categories'

    def __str__(self):
        return self.name


class Hazard(AuditedModel):
    """Hazards identified during risk analysis"""
    SOURCE_CHOICES = (
        ('design', 'Design'),
        ('manufacturing', 'Manufacturing'),
        ('use', 'Use'),
        ('environmental', 'Environmental'),
        ('software', 'Software'),
    )

    STATUS_CHOICES = (
        ('identified', 'Identified'),
        ('assessed', 'Assessed'),
        ('mitigated', 'Mitigated'),
        ('accepted', 'Accepted'),
        ('monitored', 'Monitored'),
    )

    hazard_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        RiskCategory,
        on_delete=models.PROTECT,
        related_name='hazards'
    )
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    harm_description = models.TextField()
    affected_population = models.CharField(max_length=500, blank=True, null=True)
    severity_of_harm = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='identified'
    )
    linked_complaint = models.ForeignKey(
        'complaints.Complaint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hazards'
    )
    linked_deviation = models.ForeignKey(
        'deviations.Deviation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hazards'
    )
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hazards'
    )
    department = models.ForeignKey(
        'users.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hazards'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Hazard'
        verbose_name_plural = 'Hazards'
        indexes = [
            models.Index(fields=['hazard_id']),
            models.Index(fields=['status']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f"{self.hazard_id}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.hazard_id:
            last = Hazard.objects.order_by('-id').first()
            num = 1 if not last else int(last.hazard_id.split('-')[1]) + 1
            self.hazard_id = f"HAZ-{num:04d}"
        super().save(*args, **kwargs)


class RiskAssessment(AuditedModel):
    """Risk assessment results using severity, occurrence, and detection"""
    ASSESSMENT_TYPE_CHOICES = (
        ('initial', 'Initial'),
        ('residual', 'Residual'),
        ('post_market', 'Post-Market'),
    )

    ACCEPTABILITY_CHOICES = (
        ('acceptable', 'Acceptable'),
        ('alara', 'ALARA'),
        ('unacceptable', 'Unacceptable'),
        ('conditional', 'Conditional'),
    )

    hazard = models.ForeignKey(
        Hazard,
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )
    assessment_type = models.CharField(
        max_length=50,
        choices=ASSESSMENT_TYPE_CHOICES
    )
    severity = models.IntegerField()  # 1-5
    occurrence = models.IntegerField()  # 1-5
    detection = models.IntegerField()  # 1-5
    acceptability = models.CharField(
        max_length=50,
        choices=ACCEPTABILITY_CHOICES
    )
    justification = models.TextField(blank=True, null=True)
    assessed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_assessments'
    )
    assessment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assessment_date']
        verbose_name = 'Risk Assessment'
        verbose_name_plural = 'Risk Assessments'
        unique_together = ['hazard', 'assessment_type']

    def __str__(self):
        return f"{self.hazard.hazard_id} - {self.assessment_type}"

    @property
    def rpn(self):
        """Risk Priority Number: Severity × Occurrence × Detection"""
        return (self.severity or 0) * (self.occurrence or 0) * (self.detection or 0)

    @property
    def risk_level(self):
        """Calculate risk level based on RPN thresholds"""
        rpn_value = self.rpn
        if rpn_value >= 100:
            return 'critical'
        elif rpn_value >= 50:
            return 'high'
        elif rpn_value >= 20:
            return 'medium'
        else:
            return 'low'


class RiskMitigation(AuditedModel):
    """Mitigation actions to reduce risks"""
    MITIGATION_TYPE_CHOICES = (
        ('design_change', 'Design Change'),
        ('process_control', 'Process Control'),
        ('labeling_warning', 'Labeling/Warning'),
        ('training', 'Training'),
        ('protective_measure', 'Protective Measure'),
    )

    IMPLEMENTATION_STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('implemented', 'Implemented'),
        ('verified', 'Verified'),
    )

    hazard = models.ForeignKey(
        Hazard,
        on_delete=models.CASCADE,
        related_name='mitigations'
    )
    mitigation_type = models.CharField(
        max_length=50,
        choices=MITIGATION_TYPE_CHOICES
    )
    description = models.TextField()
    implementation_status = models.CharField(
        max_length=50,
        choices=IMPLEMENTATION_STATUS_CHOICES,
        default='planned'
    )
    verification_method = models.TextField(blank=True, null=True)
    verification_result = models.TextField(blank=True, null=True)
    linked_change_control = models.ForeignKey(
        'change_controls.ChangeControl',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_mitigations'
    )
    linked_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_mitigations'
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_mitigations'
    )
    target_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Risk Mitigation'
        verbose_name_plural = 'Risk Mitigations'
        indexes = [
            models.Index(fields=['implementation_status']),
        ]

    def __str__(self):
        return f"{self.hazard.hazard_id} - {self.mitigation_type}"


class FMEAWorksheet(AuditedModel):
    """Failure Mode and Effects Analysis worksheet"""
    FMEA_TYPE_CHOICES = (
        ('design', 'Design FMEA'),
        ('process', 'Process FMEA'),
        ('use', 'Use FMEA'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded'),
    )

    fmea_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fmea_worksheets'
    )
    description = models.TextField(blank=True, null=True)
    fmea_type = models.CharField(max_length=50, choices=FMEA_TYPE_CHOICES)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_fmea_worksheets'
    )
    approval_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'FMEA Worksheet'
        verbose_name_plural = 'FMEA Worksheets'
        indexes = [
            models.Index(fields=['fmea_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.fmea_id}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.fmea_id:
            last = FMEAWorksheet.objects.order_by('-id').first()
            num = 1 if not last else int(last.fmea_id.split('-')[1]) + 1
            self.fmea_id = f"FMEA-{num:04d}"
        super().save(*args, **kwargs)


class FMEARecord(AuditedModel):
    """Individual FMEA record within a worksheet"""
    worksheet = models.ForeignKey(
        FMEAWorksheet,
        on_delete=models.CASCADE,
        related_name='records'
    )
    item_function = models.CharField(max_length=255)
    failure_mode = models.CharField(max_length=255)
    failure_effect = models.TextField()
    failure_cause = models.TextField()
    current_controls_prevention = models.TextField(blank=True, null=True)
    current_controls_detection = models.TextField(blank=True, null=True)
    severity = models.IntegerField()  # 1-10
    occurrence = models.IntegerField()  # 1-10
    detection = models.IntegerField()  # 1-10
    recommended_action = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    new_severity = models.IntegerField(blank=True, null=True)  # 1-10
    new_occurrence = models.IntegerField(blank=True, null=True)  # 1-10
    new_detection = models.IntegerField(blank=True, null=True)  # 1-10
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fmea_records'
    )
    target_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['worksheet', 'created_at']
        verbose_name = 'FMEA Record'
        verbose_name_plural = 'FMEA Records'

    def __str__(self):
        return f"{self.worksheet.fmea_id} - {self.failure_mode}"

    @property
    def rpn(self):
        """Initial Risk Priority Number"""
        return (self.severity or 0) * (self.occurrence or 0) * (self.detection or 0)

    @property
    def new_rpn(self):
        """New RPN after mitigation"""
        if self.new_severity and self.new_occurrence and self.new_detection:
            return self.new_severity * self.new_occurrence * self.new_detection
        return None


class RiskReport(AuditedModel):
    """Comprehensive risk management reports"""
    REPORT_TYPE_CHOICES = (
        ('initial_risk_analysis', 'Initial Risk Analysis'),
        ('risk_management_report', 'Risk Management Report'),
        ('post_market_update', 'Post-Market Update'),
        ('benefit_risk_analysis', 'Benefit-Risk Analysis'),
    )

    ACCEPTABILITY_CHOICES = (
        ('acceptable', 'Acceptable'),
        ('not_acceptable', 'Not Acceptable'),
        ('conditionally_acceptable', 'Conditionally Acceptable'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
    )

    report_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100, choices=REPORT_TYPE_CHOICES)
    product_line = models.ForeignKey(
        'users.ProductLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_reports'
    )
    description = models.TextField(blank=True, null=True)
    overall_risk_acceptability = models.CharField(
        max_length=50,
        choices=ACCEPTABILITY_CHOICES
    )
    benefit_risk_conclusion = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft'
    )
    linked_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='risk_reports'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Risk Report'
        verbose_name_plural = 'Risk Reports'
        indexes = [
            models.Index(fields=['report_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.report_id}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.report_id:
            last = RiskReport.objects.order_by('-id').first()
            num = 1 if not last else int(last.report_id.split('-')[1]) + 1
            self.report_id = f"RR-{num:04d}"
        super().save(*args, **kwargs)


class RiskMonitoringAlert(AuditedModel):
    """Alerts for risk monitoring and post-market surveillance"""
    ALERT_TYPE_CHOICES = (
        ('threshold_breach', 'Threshold Breach'),
        ('trend_detected', 'Trend Detected'),
        ('new_complaint', 'New Complaint'),
        ('occurrence_exceeded', 'Occurrence Exceeded'),
    )

    hazard = models.ForeignKey(
        Hazard,
        on_delete=models.CASCADE,
        related_name='monitoring_alerts'
    )
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    message = models.TextField()
    threshold_value = models.CharField(max_length=255, blank=True, null=True)
    actual_value = models.CharField(max_length=255, blank=True, null=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_risk_alerts'
    )
    acknowledged_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Risk Monitoring Alert'
        verbose_name_plural = 'Risk Monitoring Alerts'
        indexes = [
            models.Index(fields=['is_acknowledged']),
            models.Index(fields=['alert_type']),
        ]

    def __str__(self):
        return f"{self.hazard.hazard_id} - {self.alert_type}"
