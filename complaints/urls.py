from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ComplaintViewSet,
    ComplaintAttachmentViewSet,
    MIRRecordViewSet,
    ComplaintCommentViewSet,
    PMSPlanViewSet,
    TrendAnalysisViewSet,
    PMSReportViewSet,
    VigilanceReportViewSet,
    LiteratureReviewViewSet,
    SafetySignalViewSet,
)

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'complaint-attachments', ComplaintAttachmentViewSet, basename='complaint-attachment')
router.register(r'mir-records', MIRRecordViewSet, basename='mir-record')
router.register(r'complaint-comments', ComplaintCommentViewSet, basename='complaint-comment')
router.register(r'pms-plans', PMSPlanViewSet, basename='pms-plan')
router.register(r'trend-analyses', TrendAnalysisViewSet, basename='trend-analysis')
router.register(r'pms-reports', PMSReportViewSet, basename='pms-report')
router.register(r'vigilance-reports', VigilanceReportViewSet, basename='vigilance-report')
router.register(r'literature-reviews', LiteratureReviewViewSet, basename='literature-review')
router.register(r'safety-signals', SafetySignalViewSet, basename='safety-signal')

app_name = 'complaints'

urlpatterns = [
    path('', include(router.urls)),
]
