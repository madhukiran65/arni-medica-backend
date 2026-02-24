from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class AIInsight(models.Model):
    INSIGHT_TYPE_CHOICES = (
        ('prediction', 'Prediction'),
        ('recommendation', 'Recommendation'),
        ('classification', 'Classification'),
        ('risk_alert', 'Risk Alert'),
    )

    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    confidence = models.IntegerField()  # 0-100
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    model_used = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_acted_upon = models.BooleanField(default=False)
    action_taken = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Insight'
        verbose_name_plural = 'AI Insights'

    def __str__(self):
        return f"{self.insight_type.title()} - {self.title}"
