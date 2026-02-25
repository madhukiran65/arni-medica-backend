from rest_framework import serializers
from .models import (
    Supplier,
    SupplierEvaluation,
    SupplierDocument,
    SupplierCorrectiveAction,
)


class SupplierCorrectiveActionSerializer(serializers.ModelSerializer):
    """Serializer for supplier corrective actions."""
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = SupplierCorrectiveAction
        fields = [
            'id',
            'supplier',
            'description',
            'action_type',
            'assigned_to',
            'assigned_to_username',
            'due_date',
            'status',
            'completion_date',
            'comments',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'assigned_to_username']


class SupplierDocumentSerializer(serializers.ModelSerializer):
    """Serializer for supplier documents."""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SupplierDocument
        fields = [
            'id',
            'supplier',
            'document_name',
            'document_type',
            'file',
            'file_url',
            'uploaded_by',
            'uploaded_by_username',
            'uploaded_at',
            'expiry_date',
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_username']

    def get_file_url(self, obj):
        """Get absolute file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class SupplierEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for supplier evaluations."""
    evaluated_by_username = serializers.CharField(
        source='evaluated_by.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = SupplierEvaluation
        fields = [
            'id',
            'supplier',
            'evaluation_date',
            'evaluation_type',
            'score',
            'status',
            'evaluated_by',
            'evaluated_by_username',
            'comments',
            'findings',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'evaluated_by_username']


class SupplierCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating suppliers."""

    class Meta:
        model = Supplier
        fields = [
            'id',
            'supplier_id',
            'name',
            'contact_person',
            'email',
            'phone_number',
            'address',
            'supplier_type',
            'qualification_status',
            'risk_level',
            'created_at',
        ]
        read_only_fields = ['id', 'supplier_id', 'created_at']


class SupplierListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing suppliers."""

    class Meta:
        model = Supplier
        fields = [
            'id',
            'supplier_id',
            'name',
            'supplier_type',
            'qualification_status',
            'risk_level',
        ]
        read_only_fields = ['id', 'supplier_id']


class SupplierDetailSerializer(serializers.ModelSerializer):
    """Full serializer for supplier details with evaluations, documents, and corrective actions."""
    evaluations = SupplierEvaluationSerializer(
        source='supplierevaluation_set',
        many=True,
        read_only=True
    )
    documents = SupplierDocumentSerializer(
        source='supplierdocument_set',
        many=True,
        read_only=True
    )
    corrective_actions = SupplierCorrectiveActionSerializer(
        source='suppliercorrectiveaction_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Supplier
        fields = [
            'id',
            'supplier_id',
            'name',
            'contact_person',
            'email',
            'phone_number',
            'address',
            'supplier_type',
            'qualification_status',
            'risk_level',
            'last_evaluation_date',
            'notes',
            'created_at',
            'updated_at',
            'evaluations',
            'documents',
            'corrective_actions',
        ]
        read_only_fields = [
            'id',
            'supplier_id',
            'created_at',
            'updated_at',
        ]
