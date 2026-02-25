from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIInsightViewSet,
    DashboardView,
    KPIView,
    CAPATrendsView,
    ComplaintTrendsView,
    DeviationTrendsView,
    RiskMatrixView,
    QualityScoreView,
    ComplianceView,
    PredictionsView,
)

router = DefaultRouter()
router.register(r'insights', AIInsightViewSet, basename='ai-insight')

urlpatterns = [
    path('', include(router.urls)),
    # Dashboard endpoints
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('kpis/', KPIView.as_view(), name='kpis'),
    # Trend endpoints
    path('trends/capa/', CAPATrendsView.as_view(), name='capa-trends'),
    path('trends/complaints/', ComplaintTrendsView.as_view(), name='complaint-trends'),
    path('trends/deviations/', DeviationTrendsView.as_view(), name='deviation-trends'),
    # Risk and Quality endpoints
    path('risk-matrix/', RiskMatrixView.as_view(), name='risk-matrix'),
    path('quality-score/', QualityScoreView.as_view(), name='quality-score'),
    # Compliance endpoints
    path('compliance/', ComplianceView.as_view(), name='compliance'),
    # Predictions endpoint
    path('predictions/', PredictionsView.as_view(), name='predictions'),
]
