from rest_framework.permissions import BasePermission

from .services import is_conversation_member

class IsConversationMember(BasePermission):
    """
    Allows access only to conversation members.
    """

    message = (
        "You do not have permission to access this conversation."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return is_conversation_member(
            obj,
            request.user,
        )
    
class IsMessageSender(BasePermission):
    """
    Allows access only to the sender
    of a message.
    """

    message = (
        "You do not have permission to modify this message."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return obj.sender == request.user

