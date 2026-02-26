from rest_framework import serializers
from django.contrib.auth.models import User
from equipment.models import (
    Equipment,
    EquipmentQualification,
    CalibrationSchedule,
    CalibrationRecord,
    MaintenanceSchedule,
    MaintenanceRecord,
    EquipmentDocument,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)


# Equipment Serializers
class EquipmentListSerializer(serializers.ModelSerializer):
    equipment_type_display = serializers.CharField(source='get_equipment_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticality_display', read_only=True)

    class Meta:
        model = Equipment
        fields = (
            'id', 'equipment_id', 'name', 'equipment_type', 'equipment_type_display',
            'category', 'category_display', 'serial_number', 'manufacturer',
            'status', 'status_display', 'criticality', 'criticality_display',
            'requires_calibration', 'requires_maintenance', 'created_at'
        )
        read_only_fields = ('id', 'equipment_id', 'created_at')


class EquipmentDetailSerializer(serializers.ModelSerializer):
    equipment_type_display = serializers.CharField(source='get_equipment_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticality_display', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Equipment
        fields = (
            'id', 'equipment_id', 'name', 'description', 'equipment_type',
            'equipment_type_display', 'category', 'category_display', 'serial_number',
            'model_number', 'manufacturer', 'location', 'site', 'site_name',
            'department', 'department_name', 'status', 'status_display',
            'criticality', 'criticality_display', 'purchase_date', 'installation_date',
            'warranty_expiry', 'requires_calibration', 'requires_maintenance',
            'qr_code', 'notes', 'created_at', 'updated_at', 'created_by', 'updated_by'
        )
        read_only_fields = ('id', 'equipment_id', 'created_at', 'updated_at', 'created_by', 'updated_by')


# Equipment Qualification Serializers
class EquipmentQualificationListSerializer(serializers.ModelSerializer):
    qualification_type_display = serializers.CharField(source='get_qualification_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = EquipmentQualification
        fields = (
            'id', 'qualification_id', 'equipment', 'equipment_name',
            'qualification_type', 'qualification_type_display', 'result',
            'result_display', 'status', 'status_display', 'execution_date', 'created_at'
        )
        read_only_fields = ('id', 'qualification_id', 'created_at')


class EquipmentQualificationDetailSerializer(serializers.ModelSerializer):
    qualification_type_display = serializers.CharField(source='get_qualification_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    qualified_by_name = UserSerializer(source='qualified_by', read_only=True)
    approved_by_name = UserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = EquipmentQualification
        fields = (
            'id', 'qualification_id', 'equipment', 'qualification_type',
            'qualification_type_display', 'protocol_number', 'protocol_file',
            'result_file', 'execution_date', 'result', 'result_display',
            'deviations_noted', 'qualified_by', 'qualified_by_name', 'approved_by',
            'approved_by_name', 'status', 'status_display', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'qualification_id', 'created_at', 'updated_at')


# Calibration Schedule Serializers
class CalibrationScheduleSerializer(serializers.ModelSerializer):
    responsible_person_name = UserSerializer(source='responsible_person', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()

    class Meta:
        model = CalibrationSchedule
        fields = (
            'id', 'equipment', 'equipment_name', 'interval_days', 'tolerance_specs',
            'calibration_method', 'reference_standards', 'last_calibrated', 'next_due',
            'auto_quarantine_on_overdue', 'reminder_days_before', 'responsible_person',
            'responsible_person_name', 'is_overdue', 'days_until_due', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def get_days_until_due(self, obj):
        return obj.days_until_due()


# Calibration Record Serializers
class CalibrationRecordListSerializer(serializers.ModelSerializer):
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    calibration_type_display = serializers.CharField(source='get_calibration_type_display', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = CalibrationRecord
        fields = (
            'id', 'calibration_id', 'equipment', 'equipment_name', 'calibration_date',
            'result', 'result_display', 'calibration_type', 'calibration_type_display',
            'certificate_number', 'created_at'
        )
        read_only_fields = ('id', 'calibration_id', 'created_at')


class CalibrationRecordDetailSerializer(serializers.ModelSerializer):
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    calibration_type_display = serializers.CharField(source='get_calibration_type_display', read_only=True)
    performed_by_internal_name = UserSerializer(source='performed_by_internal', read_only=True)
    approved_by_name = UserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = CalibrationRecord
        fields = (
            'id', 'calibration_id', 'equipment', 'calibration_date', 'as_found_data',
            'as_left_data', 'result', 'result_display', 'certificate_number',
            'certificate_file', 'performed_by_internal', 'performed_by_internal_name',
            'performed_by_vendor', 'calibration_type', 'calibration_type_display',
            'approved_by', 'approved_by_name', 'notes', 'linked_deviation',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'calibration_id', 'created_at', 'updated_at')


# Maintenance Schedule Serializers
class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    responsible_person_name = UserSerializer(source='responsible_person', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceSchedule
        fields = (
            'id', 'equipment', 'equipment_name', 'maintenance_type',
            'maintenance_type_display', 'interval_days', 'description',
            'last_performed', 'next_due', 'responsible_person',
            'responsible_person_name', 'is_overdue', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_is_overdue(self, obj):
        return obj.is_overdue()


# Maintenance Record Serializers
class MaintenanceRecordListSerializer(serializers.ModelSerializer):
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = (
            'id', 'maintenance_id', 'equipment', 'equipment_name', 'maintenance_date',
            'maintenance_type', 'maintenance_type_display', 'status', 'status_display',
            'performed_by', 'downtime_hours', 'created_at'
        )
        read_only_fields = ('id', 'maintenance_id', 'created_at')


class MaintenanceRecordDetailSerializer(serializers.ModelSerializer):
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    performed_by_name = UserSerializer(source='performed_by', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = (
            'id', 'maintenance_id', 'equipment', 'maintenance_date', 'maintenance_type',
            'maintenance_type_display', 'description', 'work_performed', 'parts_replaced',
            'performed_by', 'performed_by_name', 'downtime_hours', 'status',
            'status_display', 'linked_deviation', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'maintenance_id', 'created_at', 'updated_at')


# Equipment Document Serializers
class EquipmentDocumentListSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = EquipmentDocument
        fields = (
            'id', 'equipment', 'equipment_name', 'document_type',
            'document_type_display', 'title', 'expiry_date', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class EquipmentDocumentDetailSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    uploaded_by_name = UserSerializer(source='uploaded_by', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentDocument
        fields = (
            'id', 'equipment', 'document_type', 'document_type_display', 'title',
            'file', 'expiry_date', 'uploaded_by', 'uploaded_by_name', 'is_expired',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_is_expired(self, obj):
        return obj.is_expired()
