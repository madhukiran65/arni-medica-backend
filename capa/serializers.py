from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CAPA, CAPAAction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class CAPAActionSerializer(serializers.ModelSerializer):
    responsible_name = serializers.CharField(source='responsible.get_full_name', read_only=True)
    
    class Meta:
        model = CAPAAction
        fields = [
            'id', 'capa', 'action_type', 'description', 'responsible', 'responsible_name',
            'target_date', 'completion_date', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CAPASerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    actions = CAPAActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = CAPA
        fields = [
            'id', 'capa_id', 'title', 'source', 'priority', 'owner', 'owner_name',
            'status', 'due_date', 'completed_date', 'description', 'root_cause',
            'root_cause_analysis_method', 'corrective_actions', 'preventive_actions',
            'verification_method', 'verification_results', 'verification_date',
            'ai_root_cause', 'ai_confidence', 'actions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CAPATransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=['investigation', 'root_cause_analysis', 'action_planning', 'effectiveness_verification', 'closed']
    )
    signature = serializers.CharField(required=False, allow_blank=True)
