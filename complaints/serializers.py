from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Complaint, ComplaintInvestigation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ComplaintInvestigationSerializer(serializers.ModelSerializer):
    investigator_name = serializers.CharField(source='investigator.get_full_name', read_only=True)
    
    class Meta:
        model = ComplaintInvestigation
        fields = [
            'id', 'complaint', 'investigator', 'investigator_name', 'investigation_step',
            'findings', 'investigation_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'investigation_date', 'created_at', 'updated_at']


class ComplaintSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    investigations = ComplaintInvestigationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'complaint_id', 'product', 'batch_lot', 'customer', 'description',
            'severity', 'status', 'reportable', 'assigned_to', 'assigned_to_name',
            'complaint_date', 'investigation_summary', 'root_cause', 'impact_assessment',
            'related_capa', 'ai_triage', 'ai_confidence', 'investigations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComplaintInvestigateSerializer(serializers.Serializer):
    investigation_step = serializers.CharField(max_length=255)
    findings = serializers.CharField()
    investigator_id = serializers.IntegerField(required=False)


class ComplaintCreateCAPASerializer(serializers.Serializer):
    capa_title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    priority = serializers.ChoiceField(choices=['critical', 'high', 'medium', 'low'])


class ComplaintCloseSerializer(serializers.Serializer):
    investigation_summary = serializers.CharField()
    root_cause = serializers.CharField(required=False, allow_blank=True)
    impact_assessment = serializers.CharField(required=False, allow_blank=True)
