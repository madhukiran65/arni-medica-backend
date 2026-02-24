from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import AuditLogViewSet

router = DefaultRouter()
router.register('', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', include(router.urls)),
]
