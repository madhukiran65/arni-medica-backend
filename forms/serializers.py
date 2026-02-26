from rest_framework import serializers
from .models import (
    FormTemplate,
    FormSection,
    FormQuestion,
    FormInstance,
    FormResponse,
    ConditionalRule,
)


class ConditionalRuleSerializer(serializers.ModelSerializer):
    """Serializer for conditional rules."""
    condition_type_display = serializers.CharField(source='get_condition_type_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    form_question_text = serializers.CharField(source='form_question.question_text', read_only=True)
    target_question_text = serializers.CharField(source='target_question.question_text', read_only=True)

    class Meta:
        model = ConditionalRule
        fields = [
            'id',
            'form_question',
            'form_question_text',
            'condition_type',
            'condition_type_display',
            'condition_value',
            'target_question',
            'target_question_text',
            'action',
            'action_display',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FormQuestionSerializer(serializers.ModelSerializer):
    """Serializer for form questions."""
    conditional_rules = ConditionalRuleSerializer(many=True, read_only=True)
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)

    class Meta:
        model = FormQuestion
        fields = [
            'id',
            'section',
            'question_text',
            'question_type',
            'question_type_display',
            'is_required',
            'sequence',
            'help_text',
            'options',
            'validation_rules',
            'default_value',
            'placeholder',
            'scoring_weight',
            'conditions',
            'conditional_rules',
        ]
        read_only_fields = ['id']


class FormSectionSerializer(serializers.ModelSerializer):
    """Serializer for form sections with nested questions."""
    questions = FormQuestionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = FormSection
        fields = [
            'id',
            'template',
            'title',
            'description',
            'sequence',
            'is_repeatable',
            'conditions',
            'questions',
        ]
        read_only_fields = ['id']


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
            'is_active',
            'category',
        ]
        read_only_fields = ['id']


class FormTemplateDetailSerializer(serializers.ModelSerializer):
    """Full serializer for form template details with nested sections and questions."""
    sections = FormSectionSerializer(
        many=True,
        read_only=True
    )
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)

    class Meta:
        model = FormTemplate
        fields = [
            'id',
            'name',
            'description',
            'template_type',
            'template_type_display',
            'version',
            'is_published',
            'is_active',
            'department',
            'category',
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
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    class Meta:
        model = FormResponse
        fields = [
            'id',
            'instance',
            'question',
            'question_text',
            'question_type',
            'response_text',
            'response_number',
            'response_boolean',
            'response_json',
            'response_file',
            'answered_at',
        ]
        read_only_fields = ['id', 'answered_at', 'question_text', 'question_type']


class FormInstanceListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing form instances."""
    template_name = serializers.CharField(source='template.name', read_only=True)
    completed_by_username = serializers.CharField(
        source='completed_by.username',
        read_only=True,
        allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FormInstance
        fields = [
            'id',
            'template_name',
            'completed_by_username',
            'status',
            'status_display',
            'completed_at',
            'score',
        ]
        read_only_fields = ['id', 'template_name', 'completed_by_username', 'status_display']


class FormInstanceDetailSerializer(serializers.ModelSerializer):
    """Full serializer for form instance details with nested responses."""
    template_name = serializers.CharField(source='template.name', read_only=True)
    completed_by_username = serializers.CharField(
        source='completed_by.username',
        read_only=True,
        allow_null=True
    )
    responses = FormResponseSerializer(
        many=True,
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FormInstance
        fields = [
            'id',
            'template',
            'template_name',
            'completed_by',
            'completed_by_username',
            'status',
            'status_display',
            'score',
            'total_possible_score',
            'context_type',
            'context_id',
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
            'status_display',
        ]


class SubmitFormSerializer(serializers.Serializer):
    """Serializer for submitting form responses."""
    responses = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField(),
        ),
        help_text='List of response dictionaries with question_id and response values'
    )

    def validate_responses(self, value):
        """Validate that each response has required fields."""
        for item in value:
            if 'question_id' not in item:
                raise serializers.ValidationError(
                    'Each response must have a question_id'
                )
        return value
