from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from rest_framework.filters import SearchFilter
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    FormTemplate,
    FormInstance,
    FormQuestion,
    ConditionalRule,
    FormSection,
)
from .serializers import (
    FormTemplateListSerializer,
    FormTemplateDetailSerializer,
    FormInstanceListSerializer,
    FormInstanceDetailSerializer,
    FormQuestionSerializer,
    ConditionalRuleSerializer,
    SubmitFormSerializer,
    FormSectionSerializer,
)


class ConditionalRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Conditional Rules.
    Provides CRUD operations for form question conditional rules.
    """
    queryset = ConditionalRule.objects.all()
    serializer_class = ConditionalRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['form_question', 'target_question', 'is_active']


class FormTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Form Templates.
    Supports publishing, duplicating, and filtering by type and department.
    """
    queryset = FormTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['template_type', 'is_published', 'department', 'created_by']
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormTemplateDetailSerializer
        elif self.action == 'list':
            return FormTemplateListSerializer
        return FormTemplateDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a form template.
        Validates that template has at least one section with one question.
        """
        template = self.get_object()

        # Validate template structure
        if not template.sections.exists():
            return Response(
                {'detail': 'Cannot publish template without sections'},
                status=status.HTTP_400_BAD_REQUEST
            )

        has_questions = FormQuestion.objects.filter(section__template=template).exists()
        if not has_questions:
            return Response(
                {'detail': 'Cannot publish template without questions'},
                status=status.HTTP_400_BAD_REQUEST
            )

        template.is_published = True
        template.save()

        serializer = self.get_serializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a form template with all sections and questions.
        Creates a deep copy preserving all relationships.
        """
        template = self.get_object()

        # Create a copy of the template
        new_template = FormTemplate.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            template_type=template.template_type,
            department=template.department,
            category=template.category,
            version=template.version,
            is_published=False,
            is_active=template.is_active,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

        # Deep copy sections and questions
        for section in template.sections.all():
            new_section = FormSection.objects.create(
                template=new_template,
                title=section.title,
                description=section.description,
                sequence=section.sequence,
                is_repeatable=section.is_repeatable,
                conditions=section.conditions,
            )

            for question in section.questions.all():
                FormQuestion.objects.create(
                    section=new_section,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    help_text=question.help_text,
                    is_required=question.is_required,
                    sequence=question.sequence,
                    options=question.options,
                    validation_rules=question.validation_rules,
                    default_value=question.default_value,
                    placeholder=question.placeholder,
                    scoring_weight=question.scoring_weight,
                    conditions=question.conditions,
                )

        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get full template structure for preview (sections + questions + conditional rules).
        """
        template = self.get_object()
        serializer = FormTemplateDetailSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def form_stats(self, request):
        """
        Get aggregated statistics on form templates.
        Returns: total templates, by type, total responses.
        """
        templates = self.get_queryset()

        stats = {
            'total_templates': templates.count(),
            'published': templates.filter(is_published=True).count(),
            'draft': templates.filter(is_published=False).count(),
            'by_type': dict(
                templates.values('template_type').annotate(count=Count('id')).values_list('template_type', 'count')
            ),
            'total_responses': FormInstance.objects.count(),
            'responses_by_status': dict(
                FormInstance.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
        }

        return Response(stats, status=status.HTTP_200_OK)


class FormInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Form Instances.
    Supports submitting form responses and filtering by template and status.
    """
    queryset = FormInstance.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template', 'status', 'completed_by', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormInstanceDetailSerializer
        elif self.action == 'list':
            return FormInstanceListSerializer
        elif self.action == 'submit':
            return SubmitFormSerializer
        return FormInstanceDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit form responses for a form instance.
        Validates that all required questions are answered.
        """
        form_instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate required questions
        required_questions = FormQuestion.objects.filter(
            section__template=form_instance.template,
            is_required=True
        )

        responses = form_instance.responses.all()
        response_question_ids = set(responses.values_list('question_id', flat=True))
        required_question_ids = set(required_questions.values_list('id', flat=True))

        missing_required = required_question_ids - response_question_ids
        if missing_required:
            return Response(
                {'detail': 'All required questions must be answered'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark as completed
        form_instance.status = 'completed'
        form_instance.completed_by = request.user
        form_instance.completed_at = timezone.now()
        form_instance.save()

        return Response(
            FormInstanceDetailSerializer(form_instance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        Export form responses in flat JSON format.
        """
        form_instance = self.get_object()

        export_data = {
            'template_name': form_instance.template.name,
            'template_type': form_instance.template.template_type,
            'status': form_instance.status,
            'completed_by': form_instance.completed_by.username if form_instance.completed_by else None,
            'completed_at': form_instance.completed_at.isoformat() if form_instance.completed_at else None,
            'responses': [],
        }

        for response in form_instance.responses.all():
            export_data['responses'].append({
                'question': response.question.question_text,
                'question_type': response.question.question_type,
                'answer': (
                    response.response_text or response.response_number or
                    response.response_boolean or response.response_json or ''
                ),
            })

        return Response(export_data, status=status.HTTP_200_OK)


class FormQuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Form Questions within a template.
    Provides CRUD operations for form questions.
    """
    queryset = FormQuestion.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FormQuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['section', 'question_type']

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
