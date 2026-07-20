"""
===============================================================================
File: admin.py
Location: backend/accounts/admin.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Registers the custom User model with Django's built-in administration site.

The Django Admin provides a secure web interface for managing database
records. By registering the custom User model, administrators can:

• View users
• Create users
• Edit users
• Delete users
• Search users
• Filter users

-------------------------------------------------------------------------------

ARCHITECTURE

Browser

    │

    ▼

Django Admin

    │

    ▼

CustomUserAdmin

    │

    ▼

User Model

    │

    ▼

PostgreSQL

-------------------------------------------------------------------------------

WHY USE UserAdmin?

Django already provides a feature-rich administration interface for its
authentication system.

Instead of creating an admin interface from scratch, ChatDen extends
Django's built-in UserAdmin to reuse its mature functionality.

-------------------------------------------------------------------------------

IMPORTANT

Only administrative presentation belongs here.

This file should NOT contain:

❌ Authentication logic
❌ Login logic
❌ JWT generation
❌ Database business rules
❌ API logic

===============================================================================
"""

# =============================================================================
# Django Imports
# =============================================================================

# Provides the registration decorator and admin framework.
from django.contrib import admin

# Django's built-in administration class for user models.
#
# We extend this instead of writing a new admin interface.
from django.contrib.auth.admin import UserAdmin


# =============================================================================
# Local Imports
# =============================================================================

# Import the custom User model that will be managed through the admin site.
from .models import User


# =============================================================================
# User Administration
# =============================================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Administration interface for the ChatDen User model.

    Inherits Django's built-in UserAdmin and customizes how users are
    displayed inside the Django Admin panel.

    This class affects only the administrator interface.

    It does NOT affect:

    • Authentication
    • API responses
    • Database schema
    • Registration
    • Login
    """

    # -------------------------------------------------------------------------
    # Default Ordering
    # -------------------------------------------------------------------------

    """
    Display users ordered by email address.

    Example:

    admin@chatden.com
    alice@example.com
    john@example.com
    """

    ordering = ("email",)

    # -------------------------------------------------------------------------
    # List View
    # -------------------------------------------------------------------------

    """
    Columns displayed on the Users list page.

    These values provide administrators with a quick overview of each
    account without opening the detail page.
    """

    list_display = (
        "email",
        "username",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    # -------------------------------------------------------------------------
    # Search Configuration
    # -------------------------------------------------------------------------

    """
    Enable searching by:

    • Email
    • Username

    This greatly improves usability when managing a large number of users.
    """

    search_fields = (
        "email",
        "username",
    )

    # -------------------------------------------------------------------------
    # Form Layout
    # -------------------------------------------------------------------------

    """
    Reuse Django's default UserAdmin field layout.

    Since ChatDen currently extends AbstractUser without introducing
    additional profile fields, the default field organization is
    sufficient.

    Future custom fields (profile picture, bio, verification status, etc.)
    can be added by extending these fieldsets.
    """

    fieldsets = UserAdmin.fieldsets