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

    class Meta:
        model = ElectronicSignature
        fields = [
            'id', 'content_type', 'object_id', 'signer', 'signer_name',
            'signed_at', 'reason', 'meaning', 'content_hash', 'signature_hash',
        ]
        read_only_fields = fields


class SignatureRequestSerializer(serializers.Serializer):
    """Used when a user signs something — requires password re-entry (21 CFR Part 11)."""
    password = serializers.CharField(write_only=True)
    reason = serializers.ChoiceField(choices=ElectronicSignature.REASON_CHOICES)
    meaning = serializers.CharField()
