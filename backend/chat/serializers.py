"""
Serializers for the Chat application.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Conversation, Message

User = get_user_model()


class ConversationSerializer(serializers.ModelSerializer):
    """
    Read serializer for Conversation objects.
    """

    class Meta:
        model = Conversation
        fields = (
            "id",
            "created_at",
        )
        read_only_fields = fields


class ConversationCreateSerializer(serializers.Serializer):
    """
    Validate input for creating or retrieving
    a direct conversation.
    """

    user_id = serializers.UUIDField()


class MessageSerializer(serializers.ModelSerializer):
    """
    Read serializer for Message objects.
    """

    sender_id = serializers.UUIDField(
        source="sender.id",
        read_only=True,
    )

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "sender_id",
            "content",
            "message_type",
            "created_at",
            "edited_at",
        )
        read_only_fields = fields


class SendMessageSerializer(serializers.Serializer):
    """
    Validate input for sending a message.
    """

    content = serializers.CharField(
        required=True,
        trim_whitespace=True,
        allow_blank=False,
        max_length=4000,  # Match this to your model field if it has a defined max_length.
    )