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
router.register(r'metrics', QualityMetricViewSet, basename='metric')
router.register(r'snapshots', MetricSnapshotViewSet, basename='metric-snapshot')
router.register(r'objectives', QualityObjectiveViewSet, basename='objective')
router.register(r'meetings', ManagementReviewMeetingViewSet, basename='meeting')
router.register(r'items', ManagementReviewItemViewSet, basename='review-item')
router.register(r'actions', ManagementReviewActionViewSet, basename='action')
router.register(r'reports', ManagementReviewReportViewSet, basename='report')
router.register(r'configurations', DashboardConfigurationViewSet, basename='dashboard-config')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
]
