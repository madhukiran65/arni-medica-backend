from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import AuditedModel
from users.models import Department


# ============================================================================
# 1. JOB FUNCTION - Hierarchical job roles
# ============================================================================
class JobFunction(AuditedModel):
    """
    Hierarchical job roles that define training requirements.
    Supports parent-child relationships for organizational structure.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_functions'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Job Function'
        verbose_name_plural = 'Job Functions'

    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================================================
# 2. TRAINING COURSE - Enhanced version
# ============================================================================
class TrainingCourse(AuditedModel):
    """
    Comprehensive training course definition supporting multiple delivery methods,
    assessments, prerequisites, and regulatory requirements.
    """
    COURSE_TYPE_CHOICES = (
        ('elearning', 'E-Learning'),
        ('on_the_job', 'On-the-Job'),
        ('classroom', 'Classroom'),
        ('read_and_understand', 'Read & Understand'),
        ('external', 'External'),
        ('blended', 'Blended'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    )

    # Existing fields
    course_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_courses'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # New enhanced fields
    course_type = models.CharField(
        max_length=50,
        choices=COURSE_TYPE_CHOICES
    )
    category = models.CharField(max_length=100, blank=True)
    duration_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    renewal_required = models.BooleanField(default=False)
    renewal_frequency_months = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    has_assessment = models.BooleanField(default=False)
    passing_score_percent = models.IntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_attempts = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)]
    )
    applicable_job_functions = models.ManyToManyField(
        JobFunction,
        blank=True,
        related_name='applicable_courses'
    )
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_courses'
    )
    scorm_package_url = models.URLField(null=True, blank=True)
    course_material = models.FileField(
        upload_to='training/course_materials/',
        null=True,
        blank=True
    )
    version = models.CharField(max_length=50, default='1.0')
    effective_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    regulatory_requirement = models.TextField(blank=True)
    trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_courses_assigned'
    )
    auto_assign_on_role_change = models.BooleanField(default=False)
    scorm_package = models.FileField(
        upload_to='scorm_packages/',
        null=True,
        blank=True,
        help_text="SCORM package file for e-learning"
    )
    classroom_attendance_required = models.BooleanField(
        default=False,
        help_text="Whether classroom attendance is required"
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Training Course'
        verbose_name_plural = 'Training Courses'

    def __str__(self):
        return f"{self.course_id} - {self.title}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate course_id."""
        if not self.course_id:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'CRS'
            last = TrainingCourse.objects.filter(course_id__startswith=f'{prefix}-{year}-').order_by('-course_id').first()
            if last and getattr(last, 'course_id'):
                try:
                    seq = int(getattr(last, 'course_id').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.course_id = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


# ============================================================================
# 3. TRAINING COMPETENCY - Add competency tracking
# ============================================================================
class TrainingCompetency(models.Model):
    """
    Competencies required for specific job functions or courses
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='competencies'
    )
    is_mandatory = models.BooleanField(default=True)
    renewal_period_months = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Training Competency'
        verbose_name_plural = 'Training Competencies'

    def __str__(self):
        return self.name


# ============================================================================
# 4. TRAINING PLAN - Auto-assign bundles
# ============================================================================
class TrainingPlan(AuditedModel):
    """
    Bundles of training courses automatically assigned to users in a job function.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    job_function = models.ForeignKey(
        JobFunction,
        on_delete=models.CASCADE,
        related_name='training_plans'
    )
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Training Plan'
        verbose_name_plural = 'Training Plans'

    def __str__(self):
        return f"{self.name} ({self.job_function.name})"


# ============================================================================
# 5. TRAINING PLAN COURSE - Through table
# ============================================================================
class TrainingPlanCourse(models.Model):
    """
    Through table linking training courses to training plans with sequencing.
    """
    training_plan = models.ForeignKey(
        TrainingPlan,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='training_plans'
    )
    sequence = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    days_until_due = models.IntegerField(default=30)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['sequence']
        unique_together = ('training_plan', 'course')
        verbose_name = 'Training Plan Course'
        verbose_name_plural = 'Training Plan Courses'

    def __str__(self):
        return f"{self.training_plan.name} - {self.course.title}"


# ============================================================================
# 6. TRAINING ASSIGNMENT - Enhanced version
# ============================================================================
class TrainingAssignment(AuditedModel):
    """
    Tracks individual training assignments with completion status,
    assessment scores, and certificate tracking.
    """
    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
        ('expired', 'Expired'),
    )

    # Existing fields
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='training_assignments'
    )
    course = models.ForeignKey(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )

    # New enhanced fields
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_training_assignments'
    )
    training_plan = models.ForeignKey(
        TrainingPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments'
    )
    attempt_count = models.IntegerField(default=0)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    time_spent_minutes = models.IntegerField(null=True, blank=True)
    completion_evidence = models.FileField(
        upload_to='training/completion_evidence/',
        null=True,
        blank=True
    )
    trainer_verification = models.BooleanField(default=False)
    trainer_verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_training_assignments'
    )
    trainer_verified_at = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=100, blank=True, unique=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    signature = models.ForeignKey(
        'core.ElectronicSignature',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_assignments'
    )
    operational_lockout = models.BooleanField(
        default=False,
        help_text="Block user from operations until training complete"
    )
    auto_triggered = models.BooleanField(
        default=False,
        help_text="Auto-triggered by SOP update"
    )
    triggering_document = models.ForeignKey(
        'documents.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='triggered_trainings',
        help_text="Document that triggered this training assignment"
    )

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'Training Assignment'
        verbose_name_plural = 'Training Assignments'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate certificate_number."""
        if not self.certificate_number and self.certificate_issued:
            from django.utils import timezone as tz
            year = tz.now().year
            prefix = 'CERT'
            last = TrainingAssignment.objects.filter(certificate_number__startswith=f'{prefix}-{year}-').order_by('-certificate_number').first()
            if last and getattr(last, 'certificate_number'):
                try:
                    seq = int(getattr(last, 'certificate_number').split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.certificate_number = f'{prefix}-{year}-{seq:04d}'
        super().save(*args, **kwargs)


# ============================================================================
# 7. TRAINING ASSESSMENT - Quiz/exam definition
# ============================================================================
class TrainingAssessment(AuditedModel):
    """
    Assessment/quiz definition for a training course.
    One-to-one relationship with TrainingCourse.
    """
    ASSESSMENT_TYPE_CHOICES = (
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('survey', 'Survey'),
        ('practical', 'Practical'),
    )

    course = models.OneToOneField(
        TrainingCourse,
        on_delete=models.CASCADE,
        related_name='assessment'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(
        max_length=50,
        choices=ASSESSMENT_TYPE_CHOICES,
        default='quiz'
    )
    passing_score = models.IntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    time_limit_minutes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )
    max_attempts = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)]
    )
    randomize_questions = models.BooleanField(default=False)
    show_correct_answers = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Training Assessment'
        verbose_name_plural = 'Training Assessments'

    def __str__(self):
        return f"{self.course.title} - Assessment"


# ============================================================================
# 8. ASSESSMENT QUESTION - 6 question types
# ============================================================================
class AssessmentQuestion(AuditedModel):
    """
    Individual assessment questions supporting multiple question types.
    """
    QUESTION_TYPE_CHOICES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('matching', 'Matching'),
        ('scenario', 'Scenario'),
    )

    assessment = models.ForeignKey(
        TrainingAssessment,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPE_CHOICES
    )
    options = models.JSONField(
        null=True,
        blank=True,
        help_text='For multiple choice: list of {text, is_correct}'
    )
    correct_answer = models.TextField(blank=True)
    points = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    sequence = models.IntegerField(validators=[MinValueValidator(1)])
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Assessment Question'
        verbose_name_plural = 'Assessment Questions'

    def __str__(self):
        return f"{self.assessment.course.title} - Q{self.sequence}"


# ============================================================================
# 9. ASSESSMENT ATTEMPT - User's attempt at assessment
# ============================================================================
class AssessmentAttempt(AuditedModel):
    """
    Tracks a user's attempt at completing an assessment.
    """
    assignment = models.ForeignKey(
        TrainingAssignment,
        on_delete=models.CASCADE,
        related_name='assessment_attempts'
    )
    assessment = models.ForeignKey(
        TrainingAssessment,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    passed = models.BooleanField(null=True, blank=True)
    attempt_number = models.IntegerField()

    class Meta:
        ordering = ['-started_at']
        unique_together = ('assignment', 'attempt_number')
        verbose_name = 'Assessment Attempt'
        verbose_name_plural = 'Assessment Attempts'

    def __str__(self):
        return f"{self.assignment.user.get_full_name()} - Attempt {self.attempt_number}"


# ============================================================================
# 10. ASSESSMENT RESPONSE - Individual answers
# ============================================================================
class AssessmentResponse(AuditedModel):
    """
    Individual answer responses during an assessment attempt.
    """
    attempt = models.ForeignKey(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        AssessmentQuestion,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    response_text = models.TextField(blank=True)
    selected_options = models.JSONField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question__sequence']
        verbose_name = 'Assessment Response'
        verbose_name_plural = 'Assessment Responses'

    def __str__(self):
        return f"{self.attempt} - Q{self.question.sequence}"


# ============================================================================
# 11. TRAINING COMPLIANCE RECORD - Compliance tracking
# ============================================================================
class TrainingComplianceRecord(AuditedModel):
    """
    Aggregated compliance metrics for users/departments during a period.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='compliance_records'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compliance_records'
    )
    total_required = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)
    total_overdue = models.IntegerField(default=0)
    compliance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    last_calculated = models.DateTimeField(auto_now=True)
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        ordering = ['-period_end']
        unique_together = ('user', 'period_start', 'period_end')
        verbose_name = 'Training Compliance Record'
        verbose_name_plural = 'Training Compliance Records'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.period_start} to {self.period_end}"
