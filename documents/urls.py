from django.urls import path, include
from rest_framework.routers import DefaultRouter
from documents.views import DocumentViewSet, DocumentChangeOrderViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'change-orders', DocumentChangeOrderViewSet, basename='document-change-order')

urlpatterns = [
    path('', include(router.urls)),
]
