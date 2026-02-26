from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RiskCategoryViewSet, HazardViewSet, RiskAssessmentViewSet,
    RiskMitigationViewSet, FMEAWorksheetViewSet, FMEARecordViewSet,
    RiskReportViewSet, RiskMonitoringAlertViewSet
)

router = DefaultRouter()
router.register(r'categories', RiskCategoryViewSet, basename='riskcategory')
router.register(r'hazards', HazardViewSet, basename='hazard')
router.register(r'assessments', RiskAssessmentViewSet, basename='riskassessment')
router.register(r'mitigations', RiskMitigationViewSet, basename='riskmitigation')
router.register(r'fmea-worksheets', FMEAWorksheetViewSet, basename='fmeaworksheet')
router.register(r'fmea-records', FMEARecordViewSet, basename='fmearecord')
router.register(r'reports', RiskReportViewSet, basename='riskreport')
router.register(r'monitoring-alerts', RiskMonitoringAlertViewSet, basename='riskmonitoringalert')

app_name = 'risk_management'

urlpatterns = [
    path('', include(router.urls)),
]
