from rest_framework import serializers
from .models import FeedbackTicket, FeedbackAttachment


class FeedbackAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = FeedbackAttachment
        fields = ['id', 'file', 'file_name', 'file_type', 'file_size',
                  'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by_name']


class FeedbackTicketListSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackTicket
        fields = ['id', 'ticket_id', 'type', 'title', 'priority', 'module',
                  'status', 'submitted_by', 'submitted_by_name',
                  'assigned_to', 'assigned_to_name',
                  'attachment_count', 'created_at', 'resolved_at']

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None

    def get_attachment_count(self, obj):
        return obj.attachments.count()


class FeedbackTicketDetailSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    attachments = FeedbackAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = FeedbackTicket
        fields = ['id', 'ticket_id', 'type', 'title', 'description',
                  'priority', 'module', 'status',
                  'submitted_by', 'submitted_by_name',
                  'assigned_to', 'assigned_to_name',
                  'resolution_summary', 'resolved_at',
                  'attachments', 'created_at', 'updated_at']

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None


class FeedbackTicketCreateSerializer(serializers.ModelSerializer):
    """Handles creation with file uploads via multipart/form-data."""

    class Meta:
        model = FeedbackTicket
        fields = ['id', 'ticket_id', 'type', 'title', 'description', 'priority', 'module']
        read_only_fields = ['id', 'ticket_id']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['submitted_by'] = request.user
        validated_data['created_by'] = request.user
        ticket = FeedbackTicket.objects.create(**validated_data)

        # Handle file uploads (files sent as file_0, file_1, file_2)
        for key in ['file_0', 'file_1', 'file_2']:
            file_obj = request.FILES.get(key)
            if file_obj:
                FeedbackAttachment.objects.create(
                    ticket=ticket,
                    file=file_obj,
                    file_name=file_obj.name,
                    file_type=getattr(file_obj, 'content_type', ''),
                    file_size=file_obj.size,
                    uploaded_by=request.user,
                )

        return ticket
