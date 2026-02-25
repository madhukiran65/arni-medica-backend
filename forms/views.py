from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import FormTemplate, FormInstance, FormQuestion
from .serializers import (
    FormTemplateListSerializer,
    FormTemplateDetailSerializer,
    FormInstanceListSerializer,
    FormInstanceDetailSerializer,
    FormQuestionSerializer,
    SubmitFormSerializer,
)


class FormTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Form Templates.
    Supports publishing, duplicating, and filtering by type and department.
    """
    queryset = FormTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template_type', 'is_published', 'department']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormTemplateDetailSerializer
        elif self.action == 'list':
            return FormTemplateListSerializer
        return FormTemplateDetailSerializer

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a form template.
        """
        template = self.get_object()
        template.is_published = True
        template.save()
        
        serializer = self.get_serializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a form template.
        """
        template = self.get_object()
        
        # Create a copy of the template
        new_template = FormTemplate.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            template_type=template.template_type,
            department=template.department,
            is_published=False,
        )
        
        # Copy associated questions and sections
        for section in template.sections.all():
            new_section = section.pk = None
            new_section.form_template = new_template
            new_section.save()
            
            for question in section.questions.all():
                new_question = question
                new_question.pk = None
                new_question.section = new_section
                new_question.save()
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FormInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Form Instances.
    Supports submitting form responses and filtering by template and status.
    """
    queryset = FormInstance.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template', 'status', 'completed_by']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormInstanceDetailSerializer
        elif self.action == 'list':
            return FormInstanceListSerializer
        elif self.action == 'submit':
            return SubmitFormSerializer
        return FormInstanceDetailSerializer

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit form responses for a form instance.
        """
        form_instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process form submission logic
        form_instance.status = 'submitted'
        form_instance.completed_by = request.user
        form_instance.save()
        
        return Response(
            FormInstanceDetailSerializer(form_instance).data,
            status=status.HTTP_200_OK
        )


class FormQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Form Questions within a template.
    Provides CRUD operations for form questions.
    """
    queryset = FormQuestion.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FormQuestionSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
