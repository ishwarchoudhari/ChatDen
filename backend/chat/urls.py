"""
URL configuration for the Chat application.
"""

from django.urls import path

from .views import ConversationDetailAPIView, ConversationListCreateAPIView, MessageListCreateAPIView

app_name = "chat"

urlpatterns = [
    path(
        "conversations/",
        ConversationListCreateAPIView.as_view(),
        name="conversation-list-create",
    ),
    path(
        "conversations/<uuid:conversation_id>/",
        ConversationDetailAPIView.as_view(),
        name="conversation-detail",
    ),
    path(
        "conversations/<uuid:conversation_id>/messages/",
        MessageListCreateAPIView.as_view(),
        name="conversation-messages",
    ),
]