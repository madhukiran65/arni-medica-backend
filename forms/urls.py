from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FormTemplateViewSet,
    FormInstanceViewSet,
    FormQuestionViewSet,
    ConditionalRuleViewSet,
)

router = DefaultRouter()
router.register(r'templates', FormTemplateViewSet, basename='form-template')
router.register(r'instances', FormInstanceViewSet, basename='form-instance')
router.register(r'questions', FormQuestionViewSet, basename='form-question')
router.register(r'conditional-rules', ConditionalRuleViewSet, basename='conditional-rule')

urlpatterns = [
    path('', include(router.urls)),
]
