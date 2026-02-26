from rest_framework import serializers
from core.models import AuditLog, Attachment, ElectronicSignature


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'content_type_name', 'object_id', 'object_repr',
            'user', 'user_name', 'action', 'timestamp',
            'ip_address', 'old_values', 'new_values', 'change_summary',
        ]
        read_only_fields = fields


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_name', 'file_type', 'file_size',
                  'file_hash', 'uploaded_by', 'uploaded_at', 'description']
        read_only_fields = ['file_hash', 'uploaded_by', 'uploaded_at']


class ElectronicSignatureSerializer(serializers.ModelSerializer):
    signer_name = serializers.CharField(source='signer.get_full_name', read_only=True)
    invalidated_by_name = serializers.CharField(
        source='invalidated_by.get_full_name', read_only=True, allow_null=True
    )
    content_type_name = serializers.CharField(
        source='content_type.model', read_only=True
    )

    class Meta:
        model = ElectronicSignature
        fields = [
            'id', 'content_type', 'content_type_name', 'object_id',
            'signer', 'signer_name', 'timestamp', 'signature_meaning', 'reason',
            'meaning', 'content_hash', 'signature_hash', 'ip_address',
            'is_valid', 'invalidated_by', 'invalidated_by_name',
            'invalidated_at', 'invalidation_reason',
        ]
        read_only_fields = fields


class SignatureRequestSerializer(serializers.Serializer):
    """Used when a user signs something — requires password re-entry (21 CFR Part 11)."""
    password = serializers.CharField(write_only=True, required=True)
    signature_meaning = serializers.ChoiceField(
        choices=ElectronicSignature.SIGNATURE_MEANING_CHOICES,
        required=True
    )
    reason = serializers.ChoiceField(
        choices=ElectronicSignature.REASON_CHOICES,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    meaning = serializers.CharField(required=True)
    content_hash = serializers.CharField(
        required=True,
        help_text="SHA-256 hash of the content being signed"
    )


class InvalidateSignatureSerializer(serializers.Serializer):
    """Used to invalidate an electronic signature with audit trail."""
    password = serializers.CharField(write_only=True, required=True)
    invalidation_reason = serializers.CharField(required=True)
