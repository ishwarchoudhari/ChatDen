"""
REST API views for the Chat application.

Views should remain thin and delegate business logic to
chat.services.
"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .permissions import IsConversationMember
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
)
from .services import (
    get_or_create_direct_conversation,
    get_user_conversations,
    get_conversation_messages,
    is_conversation_member,
    send_message,
)

from .models import Conversation

from .serializers import (
    MessageSerializer,
    SendMessageSerializer,
)


User = get_user_model()

class ConversationListCreateAPIView(APIView):
    """
    List the authenticated user's conversations or
    create/get a direct conversation.
    """

    permission_classes = (IsAuthenticated,)
    def get(self, request):
        conversations = get_user_conversations(request.user)

        serializer = ConversationSerializer(
            conversations,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    def post(self, request):
        serializer = ConversationCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        target_user = get_object_or_404(
            User,
            id=serializer.validated_data["user_id"],
        )

        conversation = get_or_create_direct_conversation(
            request.user,
            target_user,
        )

        response_serializer = ConversationSerializer(
            conversation,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
    
class ConversationDetailAPIView(APIView):
    """
    Retrieve a single conversation.
    """

    permission_classes = (IsAuthenticated,IsConversationMember,)

    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
        )

        self.check_object_permissions(
            request,
            conversation,
        )

        serializer = ConversationSerializer(conversation)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )    
class MessageListCreateAPIView(APIView):
    """
    List messages in a conversation or
    send a new message.
    """

    permission_classes = (
        IsAuthenticated,
        IsConversationMember,
    )

    def _get_conversation(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
        )

        self.check_object_permissions(
            request,
            conversation,
        )

        return conversation

    def get(self, request, conversation_id):
        """
        Retrieve all messages for a conversation.
        """
        conversation = self._get_conversation(
            request,
            conversation_id,
        )

        messages = get_conversation_messages(
            conversation,
        )

        serializer = MessageSerializer(
            messages,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, conversation_id):
        """
        Send a new message to a conversation.
        """
        conversation = self._get_conversation(
            request,
            conversation_id,
        )

        serializer = SendMessageSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        message = send_message(
            conversation=conversation,
            sender=request.user,
            content=serializer.validated_data["content"],
        )

        response_serializer = MessageSerializer(
            message,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )