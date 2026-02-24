from rest_framework import serializers
from documents.models import (
    Document,
    DocumentVersion,
    DocumentChangeOrder,
    DocumentChangeApproval,
)
from users.serializers import DepartmentSerializer


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id',
            'document',
            'version_number',
            'created_by',
            'created_by_username',
            'created_at',
            'change_summary',
            'file',
            'file_hash',
        ]
        read_only_fields = ['created_at', 'file_hash']


class DocumentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id',
            'document_id',
            'title',
            'document_type',
            'department',
            'department_name',
            'description',
            'version',
            'revision_number',
            'status',
            'effective_date',
            'next_review_date',
            'file',
            'file_hash',
            'owner',
            'owner_username',
            'requires_approval',
            'ai_classification',
            'ai_confidence',
            'versions',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['file_hash', 'created_at', 'updated_at']


class DocumentChangeApprovalSerializer(serializers.ModelSerializer):
    approver_username = serializers.CharField(source='approver.username', read_only=True)
    
    class Meta:
        model = DocumentChangeApproval
        fields = [
            'id',
            'dco',
            'approver',
            'approver_username',
            'status',
            'comments',
            'signature_hash',
            'approved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['signature_hash', 'created_at', 'updated_at']


class DocumentChangeOrderSerializer(serializers.ModelSerializer):
    affected_documents_detail = DocumentSerializer(
        source='affected_documents',
        many=True,
        read_only=True
    )
    approvals = DocumentChangeApprovalSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DocumentChangeOrder
        fields = [
            'id',
            'dco_number',
            'title',
            'reason',
            'status',
            'affected_documents',
            'affected_documents_detail',
            'change_type',
            'estimated_review_days',
            'approvals',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
