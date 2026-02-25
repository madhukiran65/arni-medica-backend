from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentInfocardTypeViewSet,
    DocumentViewSet,
    DocumentChangeOrderViewSet,
)

router = DefaultRouter()
router.register(r'infocards', DocumentInfocardTypeViewSet, basename='infocard')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'change-orders', DocumentChangeOrderViewSet, basename='change-order')

urlpatterns = [
    path('', include(router.urls)),
]
