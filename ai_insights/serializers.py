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
