from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobFunctionViewSet,
    TrainingCourseViewSet,
    TrainingPlanViewSet,
    TrainingAssignmentViewSet,
    TrainingAssessmentViewSet,
    ComplianceDashboardViewSet,
    AutoAssignView
)

router = DefaultRouter()
router.register(r'job-functions', JobFunctionViewSet, basename='job-function')
router.register(r'courses', TrainingCourseViewSet, basename='training-course')
router.register(r'plans', TrainingPlanViewSet, basename='training-plan')
router.register(r'assignments', TrainingAssignmentViewSet, basename='training-assignment')
router.register(r'assessments', TrainingAssessmentViewSet, basename='training-assessment')
router.register(r'compliance', ComplianceDashboardViewSet, basename='compliance-dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('auto-assign/', AutoAssignView.as_view(), name='auto-assign'),
]
