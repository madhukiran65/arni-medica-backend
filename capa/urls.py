from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CAPAViewSet, CAPAApprovalViewSet

router = DefaultRouter()
router.register(r'capas', CAPAViewSet, basename='capa')
router.register(r'approvals', CAPAApprovalViewSet, basename='capa-approval')

urlpatterns = [
    path('', include(router.urls)),
]
