from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize the router
router = DefaultRouter()

# Register viewsets
router.register(
    r'plans',
    views.ValidationPlanViewSet,
    basename='validation-plan'
)
router.register(
    r'validation-protocols',
    views.ValidationProtocolViewSet,
    basename='validation-protocol'
)
router.register(
    r'test-cases',
    views.ValidationTestCaseViewSet,
    basename='test-case'
)
router.register(
    r'rtm-entries',
    views.RTMEntryViewSet,
    basename='rtm-entry'
)
router.register(
    r'deviations',
    views.ValidationDeviationViewSet,
    basename='validation-deviation'
)
router.register(
    r'summary-reports',
    views.ValidationSummaryReportViewSet,
    basename='summary-report'
)

app_name = 'validation_mgmt'

urlpatterns = [
    path('', include(router.urls)),
]
