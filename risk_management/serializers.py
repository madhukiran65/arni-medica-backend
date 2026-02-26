from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    RiskCategory, Hazard, RiskAssessment, RiskMitigation,
    FMEAWorksheet, FMEARecord, RiskReport, RiskMonitoringAlert
)


# RiskCategory Serializers
class RiskCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskCategory
        fields = [
            'id', 'name', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RiskCategoryDetailSerializer(serializers.ModelSerializer):
    hazards = serializers.SerializerMethodField()

    class Meta:
        model = RiskCategory
        fields = [
            'id', 'name', 'description', 'is_active',
            'hazards', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_hazards(self, obj):
        return HazardListSerializer(
            obj.hazards.all(),
            many=True
        ).data


# Hazard Serializers
class HazardListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    assessment_count = serializers.SerializerMethodField()

    class Meta:
        model = Hazard
        fields = [
            'id', 'hazard_id', 'name', 'source', 'status',
            'category', 'category_name', 'assessment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['hazard_id', 'created_at', 'updated_at']

    def get_assessment_count(self, obj):
        return obj.risk_assessments.count()


class HazardDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
        allow_null=True
    )
    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        allow_null=True
    )
    risk_assessments = serializers.SerializerMethodField()
    mitigations = serializers.SerializerMethodField()

    class Meta:
        model = Hazard
        fields = [
            'id', 'hazard_id', 'name', 'description', 'source',
            'harm_description', 'affected_population', 'severity_of_harm',
            'status', 'category', 'category_name', 'product_line',
            'product_line_name', 'department', 'department_name',
            'linked_complaint', 'linked_deviation',
            'risk_assessments', 'mitigations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['hazard_id', 'created_at', 'updated_at']

    def get_risk_assessments(self, obj):
        return RiskAssessmentListSerializer(
            obj.risk_assessments.all(),
            many=True
        ).data

    def get_mitigations(self, obj):
        return RiskMitigationListSerializer(
            obj.mitigations.all(),
            many=True
        ).data


# RiskAssessment Serializers
class RiskAssessmentListSerializer(serializers.ModelSerializer):
    hazard_id = serializers.CharField(source='hazard.hazard_id', read_only=True)
    rpn = serializers.IntegerField(read_only=True)
    risk_level = serializers.CharField(read_only=True)

    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'hazard', 'hazard_id', 'assessment_type',
            'severity', 'occurrence', 'detection', 'rpn', 'risk_level',
            'acceptability', 'assessment_date'
        ]
        read_only_fields = ['assessment_date']


class RiskAssessmentDetailSerializer(serializers.ModelSerializer):
    hazard_id = serializers.CharField(source='hazard.hazard_id', read_only=True)
    assessed_by_name = serializers.CharField(
        source='assessed_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    rpn = serializers.IntegerField(read_only=True)
    risk_level = serializers.CharField(read_only=True)

    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'hazard', 'hazard_id', 'assessment_type',
            'severity', 'occurrence', 'detection', 'rpn', 'risk_level',
            'acceptability', 'justification', 'assessed_by',
            'assessed_by_name', 'assessment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['assessment_date', 'created_at', 'updated_at']


# RiskMitigation Serializers
class RiskMitigationListSerializer(serializers.ModelSerializer):
    hazard_id = serializers.CharField(source='hazard.hazard_id', read_only=True)
    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = RiskMitigation
        fields = [
            'id', 'hazard', 'hazard_id', 'mitigation_type',
            'implementation_status', 'responsible_person',
            'responsible_person_name', 'target_date', 'completion_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RiskMitigationDetailSerializer(serializers.ModelSerializer):
    hazard_id = serializers.CharField(source='hazard.hazard_id', read_only=True)
    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = RiskMitigation
        fields = [
            'id', 'hazard', 'hazard_id', 'mitigation_type', 'description',
            'implementation_status', 'verification_method', 'verification_result',
            'linked_change_control', 'linked_document', 'responsible_person',
            'responsible_person_name', 'target_date', 'completion_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# FMEAWorksheet Serializers
class FMEAWorksheetListSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    record_count = serializers.SerializerMethodField()

    class Meta:
        model = FMEAWorksheet
        fields = [
            'id', 'fmea_id', 'title', 'fmea_type', 'status',
            'approved_by_name', 'approval_date', 'record_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['fmea_id', 'created_at', 'updated_at']

    def get_record_count(self, obj):
        return obj.records.count()


class FMEAWorksheetDetailSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
        allow_null=True
    )
    records = serializers.SerializerMethodField()

    class Meta:
        model = FMEAWorksheet
        fields = [
            'id', 'fmea_id', 'title', 'description', 'fmea_type',
            'product_line', 'product_line_name', 'status',
            'approved_by', 'approved_by_name', 'approval_date',
            'records', 'created_at', 'updated_at'
        ]
        read_only_fields = ['fmea_id', 'created_at', 'updated_at']

    def get_records(self, obj):
        return FMEARecordListSerializer(
            obj.records.all(),
            many=True
        ).data


# FMEARecord Serializers
class FMEARecordListSerializer(serializers.ModelSerializer):
    worksheet_id = serializers.CharField(source='worksheet.fmea_id', read_only=True)
    rpn = serializers.IntegerField(read_only=True)
    new_rpn = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = FMEARecord
        fields = [
            'id', 'worksheet', 'worksheet_id', 'item_function',
            'failure_mode', 'severity', 'occurrence', 'detection',
            'rpn', 'new_severity', 'new_occurrence', 'new_detection',
            'new_rpn', 'completion_date'
        ]


class FMEARecordDetailSerializer(serializers.ModelSerializer):
    worksheet_id = serializers.CharField(source='worksheet.fmea_id', read_only=True)
    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True,
        allow_null=True
    )
    rpn = serializers.IntegerField(read_only=True)
    new_rpn = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = FMEARecord
        fields = [
            'id', 'worksheet', 'worksheet_id', 'item_function',
            'failure_mode', 'failure_effect', 'failure_cause',
            'current_controls_prevention', 'current_controls_detection',
            'severity', 'occurrence', 'detection', 'rpn',
            'recommended_action', 'action_taken',
            'new_severity', 'new_occurrence', 'new_detection', 'new_rpn',
            'responsible_person', 'responsible_person_name',
            'target_date', 'completion_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# RiskReport Serializers
class RiskReportListSerializer(serializers.ModelSerializer):
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = RiskReport
        fields = [
            'id', 'report_id', 'title', 'report_type', 'status',
            'overall_risk_acceptability', 'product_line',
            'product_line_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['report_id', 'created_at', 'updated_at']


class RiskReportDetailSerializer(serializers.ModelSerializer):
    product_line_name = serializers.CharField(
        source='product_line.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = RiskReport
        fields = [
            'id', 'report_id', 'title', 'description', 'report_type',
            'product_line', 'product_line_name', 'overall_risk_acceptability',
            'benefit_risk_conclusion', 'status', 'linked_document',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['report_id', 'created_at', 'updated_at']


# RiskMonitoringAlert Serializers
class RiskMonitoringAlertListSerializer(serializers.ModelSerializer):
    hazard_id = serializers.CharField(source='hazard.hazard_id', read_only=True)

    class Meta:
        model = RiskMonitoringAlert
        fields = [
            'id', 'hazard', 'hazard_id', 'alert_type', 'message',
            'is_acknowledged', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RiskMonitoringAlertDetailSerializer(serializers.ModelSerializer):
    hazard_id = serializers.CharField(source='hazard.hazard_id', read_only=True)
    acknowledged_by_name = serializers.CharField(
        source='acknowledged_by.get_full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = RiskMonitoringAlert
        fields = [
            'id', 'hazard', 'hazard_id', 'alert_type', 'message',
            'threshold_value', 'actual_value', 'is_acknowledged',
            'acknowledged_by', 'acknowledged_by_name', 'acknowledged_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
