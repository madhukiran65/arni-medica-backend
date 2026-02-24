from django.db import models
from django.contrib.auth.models import User


class AuditedModel(models.Model):
    """Base model with audit trail"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True


class TrainingCourse(models.Model):
    COURSE_TYPE_CHOICES = (
        ('elearning', 'E-Learning'),
        ('on_job', 'On-the-Job'),
        ('classroom', 'Classroom'),
        ('read_understand', 'Read & Understand'),
    )

    course_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_type = models.CharField(max_length=50, choices=COURSE_TYPE_CHOICES)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    renewal_frequency_months = models.IntegerField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=False)
    regulatory_requirement = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Training Course'
        verbose_name_plural = 'Training Courses'

    def __str__(self):
        return f"{self.course_id} - {self.title}"


class TrainingAssignment(AuditedModel):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('failed', 'Failed'),
    )

    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='training_assignments_assigned')
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    score = models.IntegerField(null=True, blank=True)
    passed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'Training Assignment'
        verbose_name_plural = 'Training Assignments'
        unique_together = ('course', 'assigned_to')

    def __str__(self):
        return f"{self.assigned_to.get_full_name()} - {self.course.title}"
