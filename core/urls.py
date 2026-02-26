from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    AuditLogViewSet, ElectronicSignatureViewSet, NotificationViewSet,
    health_check, setup_initial_data, send_test_email,
    export_capa_pdf, export_deviation_pdf, export_audit_pdf
)

router = DefaultRouter()
router.register('audit-logs', AuditLogViewSet, basename='auditlog')
router.register('electronic-signatures', ElectronicSignatureViewSet, basename='electronicsignature')
router.register('notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('setup/', setup_initial_data, name='setup-initial-data'),
    path('test-email/', send_test_email, name='test-email'),

    # PDF Export endpoints
    path('export/capa/<int:capa_id>/pdf/', export_capa_pdf, name='export-capa-pdf'),
    path('export/deviation/<int:deviation_id>/pdf/', export_deviation_pdf, name='export-deviation-pdf'),
    path('export/audit/<int:audit_id>/pdf/', export_audit_pdf, name='export-audit-pdf'),

    path('', include(router.urls)),
]
