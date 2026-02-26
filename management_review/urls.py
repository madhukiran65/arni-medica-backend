from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QualityMetricViewSet,
    MetricSnapshotViewSet,
    QualityObjectiveViewSet,
    ManagementReviewMeetingViewSet,
    ManagementReviewItemViewSet,
    ManagementReviewActionViewSet,
    ManagementReviewReportViewSet,
    DashboardConfigurationViewSet,
    DashboardAPIView,
)

router = DefaultRouter()
router.register(r'quality-metrics', QualityMetricViewSet, basename='metric')
router.register(r'metric-snapshots', MetricSnapshotViewSet, basename='metric-snapshot')
router.register(r'quality-objectives', QualityObjectiveViewSet, basename='objective')
router.register(r'meetings', ManagementReviewMeetingViewSet, basename='meeting')
router.register(r'review-items', ManagementReviewItemViewSet, basename='review-item')
router.register(r'actions', ManagementReviewActionViewSet, basename='action')
router.register(r'reports', ManagementReviewReportViewSet, basename='report')
router.register(r'dashboard-config', DashboardConfigurationViewSet, basename='dashboard-config')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
]
