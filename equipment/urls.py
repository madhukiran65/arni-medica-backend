from django.urls import path, include
from rest_framework.routers import DefaultRouter
from equipment.views import (
    EquipmentViewSet,
    EquipmentQualificationViewSet,
    CalibrationScheduleViewSet,
    CalibrationRecordViewSet,
    MaintenanceScheduleViewSet,
    MaintenanceRecordViewSet,
    EquipmentDocumentViewSet,
)

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'qualifications', EquipmentQualificationViewSet, basename='qualification')
router.register(r'calibration-schedules', CalibrationScheduleViewSet, basename='calibration-schedule')
router.register(r'calibration-records', CalibrationRecordViewSet, basename='calibration-record')
router.register(r'maintenance-schedules', MaintenanceScheduleViewSet, basename='maintenance-schedule')
router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='maintenance-record')
router.register(r'documents', EquipmentDocumentViewSet, basename='document')

app_name = 'equipment'

urlpatterns = [
    path('', include(router.urls)),
]
