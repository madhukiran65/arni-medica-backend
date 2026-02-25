from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import AIInsight


class AIInsightSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = AIInsight
        fields = [
            'id', 'insight_type', 'title', 'description', 'confidence',
            'severity', 'content_type', 'content_type_name', 'object_id',
            'model_used', 'created_at', 'is_acted_upon', 'action_taken'
        ]
        read_only_fields = ['id', 'created_at']

    def get_content_type_name(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None


class ModelStatusSerializer(serializers.Serializer):
    model_name = serializers.CharField()
    insight_count = serializers.IntegerField()
    high_confidence_count = serializers.IntegerField()
    acted_upon_count = serializers.IntegerField()
    accuracy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


# Serializers for dashboard responses
class QualityScoreSerializer(serializers.Serializer):
    """Serializer for quality score response"""
    overall_score = serializers.FloatField()
    breakdown = serializers.DictField()
    recommendations = serializers.ListField(child=serializers.CharField())
    rating = serializers.CharField()


class TrendDataSerializer(serializers.Serializer):
    """Serializer for trend data responses"""
    total_count = serializers.IntegerField()
    recent_count = serializers.IntegerField()
    open_count = serializers.IntegerField()
    closed_count = serializers.IntegerField()
    weekly_trends = serializers.ListField()


class KPISerializer(serializers.Serializer):
    """Serializer for KPI response"""
    capa_closure_rate_percent = serializers.FloatField()
    avg_complaint_resolution_days = serializers.FloatField()
    training_compliance_percent = serializers.FloatField()
    document_review_ontime_percent = serializers.FloatField()
    deviation_recurrence_rate_percent = serializers.FloatField()
    mdr_reporting_rate_percent = serializers.FloatField()


class RiskMatrixSerializer(serializers.Serializer):
    """Serializer for risk matrix response"""
    matrix = serializers.ListField()
    statistics = serializers.DictField()
