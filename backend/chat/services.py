"""
Business logic for the chat application.

This module contains reusable services responsible for
conversation management, membership validation,
message creation, and message retrieval.

Services are independent of HTTP, serializers,
and WebSocket consumers.

All chat business rules should be implemented here.
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, QuerySet
from .models import Conversation, ConversationMember, Message
from rest_framework.exceptions import ValidationError

User = get_user_model()


def get_or_create_direct_conversation(
    user_one: User,
    user_two: User,
) -> Conversation:
    """
    Return the existing direct conversation between two users.

    If one does not exist, create it together with its memberships.

    This service is idempotent.
    """

    if user_one == user_two:
        raise ValidationError(
            {
                "user_id": "You cannot create a conversation with yourself."
            }
        )

    with transaction.atomic():
        conversation = (
            Conversation.objects.annotate(
                member_count=Count("members"),
            )
            .filter(
                member_count=2,
                members__user=user_one,
            )
            .filter(
                members__user=user_two,
            )
            .first()
        )

        if conversation is not None:
            return conversation

        conversation = Conversation.objects.create()

        ConversationMember.objects.bulk_create(
            [
                ConversationMember(
                    conversation=conversation,
                    user=user_one,
                ),
                ConversationMember(
                    conversation=conversation,
                    user=user_two,
                ),
            ]
        )

        return conversation
    
def is_conversation_member(
    conversation: Conversation,
    user: User,
) -> bool:
    """
    Return True if the user belongs to the conversation.

    This service is the central authorization primitive for
    conversation-based operations.

    It performs no permission decisions beyond membership.
    """

    return ConversationMember.objects.filter(
        conversation=conversation,
        user=user,
    ).exists() 

def get_conversation_participants(
    conversation: Conversation,
) -> QuerySet[User]:
    """
    Return all users participating in the given conversation.

    The returned QuerySet is lazily evaluated and may be
    further filtered or optimized by callers.

    No permission checks are performed.
    """

    return User.objects.filter(
        conversation_memberships__conversation=conversation,
    ).order_by("conversation_memberships__joined_at")   


def send_message(
    conversation: Conversation,
    sender: User,
    content: str,
) -> Message:
    """
    Create and return a new text message.

    The sender must belong to the conversation.

    This service contains only business logic and is
    independent of HTTP, serializers, and WebSockets.
    """

    if not is_conversation_member(
        conversation=conversation,
        user=sender,
    ):
        raise PermissionError(
            "The sender is not a member of this conversation."
        )

    content = content.strip()

    if not content:
        raise ValueError(
            "Message content cannot be empty."
        )

    with transaction.atomic():
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content,
            message_type=Message.MessageType.TEXT,
        )

    return message

def get_conversation_messages(
    conversation: Conversation,
) -> QuerySet[Message]:
    """
    Return all messages for the given conversation.

    Messages are returned in chronological order.

    No authorization is performed by this service.
    """

    return (
        Message.objects.filter(
            conversation=conversation,
        )
        .select_related("sender")
        .order_by("created_at")
    )

def get_user_conversations(
    user: User,
) -> QuerySet[Conversation]:
    """
    Return all conversations that the user belongs to.

    Conversations are ordered by newest first.

    No authorization or pagination is performed by
    this service.
    """

    return (
        Conversation.objects.filter(
            members__user=user,
        )
        .prefetch_related(
            "members__user",
        )
        .order_by("-created_at")
        .distinct()
    )