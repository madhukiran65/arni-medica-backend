from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AuditPlan, AuditFinding


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class AuditFindingSerializer(serializers.ModelSerializer):
    assigned_capa_id = serializers.IntegerField(source='assigned_capa.id', read_only=True)
    
    class Meta:
        model = AuditFinding
        fields = [
            'id', 'audit', 'finding_id', 'category', 'description', 'evidence',
            'status', 'assigned_capa', 'assigned_capa_id', 'target_closure_date',
            'actual_closure_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'finding_id', 'created_at', 'updated_at']


class AuditPlanSerializer(serializers.ModelSerializer):
    lead_auditor_name = serializers.CharField(source='lead_auditor.get_full_name', read_only=True)
    findings = AuditFindingSerializer(many=True, read_only=True)

    class Meta:
        model = AuditPlan
        fields = [
            'id', 'audit_id', 'audit_type', 'scope', 'status',
            'planned_start_date', 'planned_end_date', 'actual_start_date',
            'actual_end_date', 'lead_auditor', 'lead_auditor_name', 'supplier',
            'findings_count', 'major_nc', 'minor_nc', 'observations',
            'next_audit_planned', 'findings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'audit_id', 'findings_count', 'major_nc', 'minor_nc', 'observations', 'created_at', 'updated_at']


class AuditCloseSerializer(serializers.Serializer):
    actual_end_date = serializers.DateField()
    next_audit_planned = serializers.DateField(required=False, allow_null=True)
