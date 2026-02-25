from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierEvaluationViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'evaluations', SupplierEvaluationViewSet, basename='supplier-evaluation')

urlpatterns = [
    path('', include(router.urls)),
]
