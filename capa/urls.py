from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CAPAViewSet, CAPAActionViewSet

router = DefaultRouter()
router.register(r'capa', CAPAViewSet, basename='capa')
router.register(r'capa-actions', CAPAActionViewSet, basename='capa-action')

urlpatterns = [
    path('', include(router.urls)),
]
