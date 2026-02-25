from rest_framework import serializers
from .models import (
    Supplier,
    SupplierEvaluation,
    SupplierDocument,
    SupplierCorrectiveAction,
)


class SupplierCorrectiveActionSerializer(serializers.ModelSerializer):
    """Serializer for supplier corrective actions."""
    verified_by_username = serializers.CharField(
        source='verified_by.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = SupplierCorrectiveAction
        fields = [
            'id',
            'supplier',
            'scar_number',
            'issue_description',
            'status',
            'response_due_date',
            'response_received_date',
            'corrective_action',
            'verification_result',
            'verified_by',
            'verified_by_username',
            'capa',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'verified_by_username']


class SupplierDocumentSerializer(serializers.ModelSerializer):
    """Serializer for supplier documents."""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SupplierDocument
        fields = [
            'id',
            'supplier',
            'title',
            'document_type',
            'file',
            'file_url',
            'expiry_date',
            'uploaded_by',
            'uploaded_by_username',
            'uploaded_at',
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
    evaluator_username = serializers.CharField(
        source='evaluator.username',
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
            'overall_score',
            'quality_score',
            'delivery_score',
            'service_score',
            'compliance_score',
            'evaluator',
            'evaluator_username',
            'comments',
            'recommendation',
            'next_evaluation_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'evaluator_username']


class SupplierCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating suppliers."""

    class Meta:
        model = Supplier
        fields = [
            'name',
            'description',
            'supplier_type',
            'contact_name',
            'contact_email',
            'contact_phone',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'website',
            'department',
            'quality_contact',
            'risk_level',
            'products_services',
            'approved_materials',
        ]


class SupplierListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing suppliers."""
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)

    class Meta:
        model = Supplier
        fields = [
            'id',
            'supplier_id',
            'name',
            'supplier_type',
            'qualification_status',
            'risk_level',
            'department_name',
            'next_evaluation_date',
        ]
        read_only_fields = ['id', 'supplier_id']


class SupplierDetailSerializer(serializers.ModelSerializer):
    """Full serializer for supplier details with evaluations, documents, and corrective actions."""
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    evaluations = SupplierEvaluationSerializer(
        many=True,
        read_only=True
    )
    documents = SupplierDocumentSerializer(
        many=True,
        read_only=True
    )
    corrective_actions = SupplierCorrectiveActionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Supplier
        fields = [
            'id',
            'supplier_id',
            'name',
            'description',
            'supplier_type',
            'contact_name',
            'contact_email',
            'contact_phone',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'website',
            'qualification_status',
            'qualified_date',
            'next_evaluation_date',
            'qualification_notes',
            'risk_level',
            'risk_justification',
            'iso_certified',
            'iso_certificate_number',
            'iso_expiry_date',
            'regulatory_registrations',
            'gmp_compliant',
            'products_services',
            'approved_materials',
            'department',
            'department_name',
            'quality_contact',
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
            'department_name',
        ]
