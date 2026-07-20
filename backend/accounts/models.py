"""
===============================================================================
File: models.py
Location: backend/accounts/models.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Defines the database models for the Accounts application.

Currently, this module contains the custom User model used throughout
the entire ChatDen application.

Every authenticated entity in ChatDen (human users, administrators,
future AI bots, etc.) will be represented by this model.

-------------------------------------------------------------------------------

WHY A CUSTOM USER MODEL?

Django provides a built-in User model, but production applications
should define a custom User model before the first migration.

Advantages:

✔ Full control over authentication
✔ Future support for Google Login
✔ Future support for Phone OTP
✔ Future support for AI Bot accounts
✔ Easy profile expansion
✔ UUID primary keys

-------------------------------------------------------------------------------

ARCHITECTURE

                    UserManager
                          │
                          ▼
                    User Model
                          │
                          ▼
                    PostgreSQL

Future modules:

Authentication
        │
JWT
        │
Chat
        │
Groups
        │
Media
        │
AI
        │
Notifications
        │
Profile

All depend on this model.

-------------------------------------------------------------------------------

IMPORTANT

Business logic should NOT be placed here.

Examples of things that do NOT belong here:

❌ Login
❌ JWT generation
❌ Email verification
❌ OTP
❌ AI processing
❌ Chat logic

Only database structure belongs here.

===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

# Used to generate universally unique identifiers (UUIDs).
#
# UUIDs are much harder to guess than sequential integer IDs,
# making them a good choice for public-facing applications.
#
import uuid


# =============================================================================
# Django Imports
# =============================================================================

# AbstractUser provides Django's complete authentication framework.
#
# We extend it instead of rewriting authentication from scratch.
#
from django.contrib.auth.models import AbstractUser

# Django ORM base classes.
from django.db import models


# =============================================================================
# Local Imports
# =============================================================================

# Custom manager responsible for creating user accounts.
from .managers import UserManager


# =============================================================================
# User Model
# =============================================================================

class User(AbstractUser):
    """
    Custom User model for ChatDen.

    Inherits Django's AbstractUser and customizes it for the project's
    authentication requirements.

    Every authenticated entity in ChatDen is represented by this model.
    """

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    """
    UUID primary key.

    Why UUID?

    Integer IDs:

        1
        2
        3
        4

    are predictable.

    UUIDs:

        7d9abdd2-8d8c-4c48...

    are effectively impossible to guess.

    This improves security for public APIs.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # -------------------------------------------------------------------------
    # Email
    # -------------------------------------------------------------------------

    """
    Primary authentication field.

    Email addresses must be unique because ChatDen uses email-based
    authentication instead of username-based authentication.
    """

    email = models.EmailField(
        unique=True,
    )

    # -------------------------------------------------------------------------
    # Authentication Configuration
    # -------------------------------------------------------------------------

    """
    Tell Django to authenticate users using their email address.

    Instead of:

        username

    ChatDen uses:

        email
    """

    USERNAME_FIELD = "email"

    """
    Fields required when creating a superuser using:

        python manage.py createsuperuser

    Since email is already the USERNAME_FIELD, only username is required
    in addition.
    """

    REQUIRED_FIELDS = ["username"]

    # -------------------------------------------------------------------------
    # Custom Manager
    # -------------------------------------------------------------------------

    """
    Attach the custom UserManager.

    All user creation should go through this manager to ensure consistent
    password hashing, email normalization, and future extensibility.
    """

    objects = UserManager()

    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------

    def __str__(self):
        """
        Return a human-readable representation of the user.

        Django Admin and debugging tools use this value.
        """

        return self.email