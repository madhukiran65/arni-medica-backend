from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import AuditLogViewSet, health_check

router = DefaultRouter()
router.register('', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]
