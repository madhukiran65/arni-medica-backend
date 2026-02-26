from django_filters import rest_framework as filters
from equipment.models import (
    Equipment,
    EquipmentQualification,
    CalibrationSchedule,
    CalibrationRecord,
    MaintenanceSchedule,
    MaintenanceRecord,
    EquipmentDocument,
)


class EquipmentFilter(filters.FilterSet):
    equipment_type = filters.ChoiceFilter(choices=Equipment.EQUIPMENT_TYPE_CHOICES)
    category = filters.ChoiceFilter(choices=Equipment.CATEGORY_CHOICES)
    status = filters.ChoiceFilter(choices=Equipment.STATUS_CHOICES)
    criticality = filters.ChoiceFilter(choices=Equipment.CRITICALITY_CHOICES)
    requires_calibration = filters.BooleanFilter()
    requires_maintenance = filters.BooleanFilter()
    manufacturer = filters.CharFilter(lookup_expr='icontains')
    serial_number = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Equipment
        fields = ('equipment_type', 'category', 'status', 'criticality', 'site', 'department')


class EquipmentQualificationFilter(filters.FilterSet):
    qualification_type = filters.ChoiceFilter(choices=EquipmentQualification.QUALIFICATION_TYPE_CHOICES)
    result = filters.ChoiceFilter(choices=EquipmentQualification.RESULT_CHOICES)
    status = filters.ChoiceFilter(choices=EquipmentQualification.STATUS_CHOICES)
    equipment__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EquipmentQualification
        fields = ('equipment', 'qualification_type', 'result', 'status')


class CalibrationScheduleFilter(filters.FilterSet):
    is_overdue = filters.BooleanFilter(method='filter_is_overdue')
    equipment__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CalibrationSchedule
        fields = ('equipment', 'auto_quarantine_on_overdue')

    def filter_is_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(next_due__lt=filters.timezone.now().date())
        return queryset.exclude(next_due__lt=filters.timezone.now().date())


class CalibrationRecordFilter(filters.FilterSet):
    result = filters.ChoiceFilter(choices=CalibrationRecord.RESULT_CHOICES)
    calibration_type = filters.ChoiceFilter(choices=CalibrationRecord.CALIBRATION_TYPE_CHOICES)
    calibration_date__gte = filters.DateFilter(field_name='calibration_date', lookup_expr='gte')
    calibration_date__lte = filters.DateFilter(field_name='calibration_date', lookup_expr='lte')
    equipment__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CalibrationRecord
        fields = ('equipment', 'result', 'calibration_type', 'performed_by_internal', 'performed_by_vendor')


class MaintenanceScheduleFilter(filters.FilterSet):
    maintenance_type = filters.ChoiceFilter(choices=MaintenanceSchedule.MAINTENANCE_TYPE_CHOICES)
    is_overdue = filters.BooleanFilter(method='filter_is_overdue')
    equipment__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = MaintenanceSchedule
        fields = ('equipment', 'maintenance_type', 'responsible_person')

    def filter_is_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(next_due__lt=filters.timezone.now().date())
        return queryset.exclude(next_due__lt=filters.timezone.now().date())


class MaintenanceRecordFilter(filters.FilterSet):
    maintenance_type = filters.ChoiceFilter(choices=MaintenanceRecord.MAINTENANCE_TYPE_CHOICES)
    status = filters.ChoiceFilter(choices=MaintenanceRecord.STATUS_CHOICES)
    maintenance_date__gte = filters.DateFilter(field_name='maintenance_date', lookup_expr='gte')
    maintenance_date__lte = filters.DateFilter(field_name='maintenance_date', lookup_expr='lte')
    equipment__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = MaintenanceRecord
        fields = ('equipment', 'maintenance_type', 'status', 'performed_by')


class EquipmentDocumentFilter(filters.FilterSet):
    document_type = filters.ChoiceFilter(choices=EquipmentDocument.DOCUMENT_TYPE_CHOICES)
    is_expired = filters.BooleanFilter(method='filter_is_expired')
    equipment__name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EquipmentDocument
        fields = ('equipment', 'document_type')

    def filter_is_expired(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(expiry_date__lt=timezone.now().date())
        return queryset.exclude(expiry_date__lt=timezone.now().date())
