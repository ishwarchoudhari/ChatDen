import uuid

from django.conf import settings
from django.db import models
# Create your models here.
class Conversation(models.Model):
    """
    Represents a direct conversation between two users.

    This model intentionally stores only conversation-level data.

    Participant-specific state (such as archived or pinned)
    belongs in ConversationMember.

    Phase 5 supports direct conversations only.
    Group conversations are intentionally deferred.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return f"Conversation {self.id}"
    
class ConversationMember(models.Model):
    """
    Represents a user's membership in a conversation.

    This model intentionally stores all participant-specific
    conversation state.

    Conversation-level data belongs in Conversation.

    Phase 5 supports direct conversations only.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversation_memberships",
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    is_archived = models.BooleanField(
        default=False,
    )

    is_pinned = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ("joined_at",)

        verbose_name = "Conversation Member"
        verbose_name_plural = "Conversation Members"

        constraints = [
            models.UniqueConstraint(
                fields=(
                    "conversation",
                    "user",
                ),
                name="unique_conversation_member",
            ),
        ]

        indexes = [
            models.Index(
                fields=("conversation",),
                name="conv_member_conv_idx"
            ),
            models.Index(
                fields=("user",),
                name="conv_member_user_idx"
            ),
        ]
    
class Message(models.Model):
    """
    Represents a single message sent within a conversation.

    This model stores only persistent message data.

    Authorization, conversation membership validation,
    duplicate prevention, delivery, notifications,
    read receipts, and realtime behavior are implemented
    in higher layers.
    """

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )

    content = models.TextField()

    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    edited_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("created_at",)
        
        verbose_name = "Message"
        verbose_name_plural = "Messages"

        indexes = [
            models.Index(
                fields=("sender",),
                name="message_sender_idx",
            ),
            models.Index(
                fields=("conversation", "created_at"),
                name="msg_conv_created_idx",
            ),
        ]
    