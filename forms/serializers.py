from rest_framework import serializers
from .models import (
    FormTemplate,
    FormSection,
    FormQuestion,
    FormInstance,
    FormResponse,
)


class FormQuestionSerializer(serializers.ModelSerializer):
    """Serializer for form questions."""

    class Meta:
        model = FormQuestion
        fields = [
            'id',
            'section',
            'question_text',
            'question_type',
            'required',
            'order',
            'help_text',
            'validation_rules',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FormSectionSerializer(serializers.ModelSerializer):
    """Serializer for form sections with nested questions."""
    questions = FormQuestionSerializer(
        source='formquestion_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = FormSection
        fields = [
            'id',
            'template',
            'section_title',
            'section_description',
            'order',
            'questions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FormTemplateListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing form templates."""

    class Meta:
        model = FormTemplate
        fields = [
            'id',
            'name',
            'template_type',
            'version',
            'is_published',
        ]
        read_only_fields = ['id']


class FormTemplateDetailSerializer(serializers.ModelSerializer):
    """Full serializer for form template details with nested sections and questions."""
    sections = FormSectionSerializer(
        source='formsection_set',
        many=True,
        read_only=True
    )
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = FormTemplate
        fields = [
            'id',
            'name',
            'description',
            'template_type',
            'version',
            'is_published',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
            'sections',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'created_by_username',
        ]


class FormResponseSerializer(serializers.ModelSerializer):
    """Serializer for form responses."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)

    class Meta:
        model = FormResponse
        fields = [
            'id',
            'form_instance',
            'question',
            'question_text',
            'response_text',
            'response_number',
            'response_boolean',
            'response_json',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'question_text']


class FormInstanceListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing form instances."""
    template_name = serializers.CharField(source='template.name', read_only=True)
    completed_by_username = serializers.CharField(
        source='completed_by.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = FormInstance
        fields = [
            'id',
            'template_name',
            'completed_by_username',
            'status',
            'completed_at',
            'score',
        ]
        read_only_fields = ['id', 'template_name', 'completed_by_username']


class FormInstanceDetailSerializer(serializers.ModelSerializer):
    """Full serializer for form instance details with nested responses."""
    template_name = serializers.CharField(source='template.name', read_only=True)
    completed_by_username = serializers.CharField(
        source='completed_by.username',
        read_only=True,
        allow_null=True
    )
    responses = FormResponseSerializer(
        source='formresponse_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = FormInstance
        fields = [
            'id',
            'template',
            'template_name',
            'completed_by',
            'completed_by_username',
            'status',
            'score',
            'completed_at',
            'created_at',
            'updated_at',
            'responses',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'template_name',
            'completed_by_username',
        ]


class SubmitFormSerializer(serializers.Serializer):
    """Serializer for submitting form responses."""
    action = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField(),
            help_text='Response data with question_id and response fields'
        ),
        help_text='List of response dictionaries with question_id and response values'
    )

    def validate_action(self, value):
        """Validate that each action item has required fields."""
        for item in value:
            if 'question_id' not in item:
                raise serializers.ValidationError(
                    'Each action item must have a question_id'
                )
        return value
