from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditPlanViewSet, AuditFindingViewSet

router = DefaultRouter()
router.register(r'audit-plans', AuditPlanViewSet, basename='audit-plan')
router.register(r'audit-findings', AuditFindingViewSet, basename='audit-finding')

urlpatterns = [
    path('', include(router.urls)),
]
