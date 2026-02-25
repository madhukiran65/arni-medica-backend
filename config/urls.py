from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # App endpoints
    path('api/users/', include('users.urls')),
    path('api/workflows/', include('workflows.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/capa/', include('capa.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/training/', include('training.urls')),
    path('api/audits/', include('audit_mgmt.urls')),
    path('api/ai/', include('ai_insights.urls')),
    path('api/audit-logs/', include('core.urls')),
    path('api/deviations/', include('deviations.urls')),
    path('api/change-controls/', include('change_controls.urls')),
    path('api/forms/', include('forms.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    # Health check
    path('api/health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
