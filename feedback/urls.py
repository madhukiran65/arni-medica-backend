from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackTicketViewSet

router = DefaultRouter()
router.register(r'tickets', FeedbackTicketViewSet, basename='feedback-ticket')

urlpatterns = [
    path('', include(router.urls)),
]
