"""
Relationship Policy Service.

This module contains the core relationship business rules for ChatDen.

IMPORTANT:
----------
This file is intentionally kept independent of Django REST Framework.

It contains ONLY domain/business logic and can be reused by:

- REST API Views
- Django Channels (WebSockets)
- Celery Tasks
- Signals
- Management Commands
- Future Notification Services
- Future Conversation Services

The service layer answers questions about relationships.

It does NOT:
- Handle HTTP requests
- Return DRF Responses
- Perform serialization
- Implement API endpoints

Keeping business rules here prevents duplication throughout
the project and ensures there is a single source of truth.
"""

from django.db import models

from accounts.models import User
from .models import Block


def is_blocked(user_a: User, user_b: User) -> bool:
    """
    Determine whether two users have a blocked relationship.

    Blocking in ChatDen is treated as BIDIRECTIONAL.

    Examples
    --------
    A blocks B
        -> True

    B blocks A
        -> True

    Neither user has blocked the other
        -> False

    Why is this implemented here?
    -----------------------------
    Future modules such as:

    - Conversations
    - Messaging
    - Presence
    - Notifications
    - Calls

    should NEVER query the Block model directly.

    Instead they should simply call:

        is_blocked(user_a, user_b)

    This keeps the blocking logic centralized and prevents
    duplicate ORM queries throughout the project.
    """

    return Block.objects.filter(
        models.Q(blocker=user_a, blocked=user_b)
        | models.Q(blocker=user_b, blocked=user_a)
    ).exists()


def can_view_profile(viewer: User, target: User) -> bool:
    """
    Determine whether ``viewer`` may access ``target``'s public profile.

    Current Phase 4 Rules
    ---------------------
    1. Inactive users are never publicly visible.
    2. Blocked users cannot view each other's profiles.

    Future Phases
    -------------
    This function is intentionally designed to grow.

    Future rules may include:

    - Private accounts
    - Friends-only visibility
    - Mutual connections
    - Custom privacy settings

    Future modules should continue calling this function
    without needing to know HOW the decision is made.
    """

    # Inactive users are never discoverable.
    if not target.is_active:
        return False

    # Blocked users cannot see each other's profiles.
    if is_blocked(viewer, target):
        return False

    return True


def can_message(sender: User, recipient: User) -> bool:
    """
    Determine whether ``sender`` may message ``recipient``.

    Current Phase 4 Rules
    ---------------------
    1. Recipient must be active.
    2. Neither participant may have blocked the other.

    NOTE
    ----
    This function intentionally DOES NOT check:

    - Conversations
    - Friend Requests
    - Privacy Settings
    - Message Requests
    - User Preferences

    Those features belong to future phases.

    By routing all messaging permission checks through this
    function, future rules can be added here without modifying
    the Messaging module.
    """

    # Users cannot send messages to inactive accounts.
    if not recipient.is_active:
        return False

    # Blocking immediately prevents messaging.
    if is_blocked(sender, recipient):
        return False

    return True