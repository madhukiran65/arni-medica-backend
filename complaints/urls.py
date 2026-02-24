from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet, ComplaintInvestigationViewSet

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'complaint-investigations', ComplaintInvestigationViewSet, basename='complaint-investigation')

urlpatterns = [
    path('', include(router.urls)),
]
