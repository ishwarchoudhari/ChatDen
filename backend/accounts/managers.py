"""
===============================================================================
File: managers.py
Location: backend/accounts/managers.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Defines the custom manager for the ChatDen User model.

The UserManager is responsible for creating all user accounts in a
consistent and secure manner.

Instead of allowing different parts of the application to create users
independently, every account should be created through this manager.

-------------------------------------------------------------------------------

WHY USE A CUSTOM USER MANAGER?

Without a custom manager:

Register API
    creates user one way

Google Login
    creates user another way

Admin Panel
    creates user differently

Phone OTP
    creates user differently

This quickly becomes inconsistent.

Instead:

Register API
        │
Google OAuth
        │
Phone OTP
        │
Admin
        │
AI Bot
        │
        ▼
UserManager
        │
        ▼
Database

One place.

One implementation.

One security policy.

-------------------------------------------------------------------------------

RESPONSIBILITIES

✔ Create regular users
✔ Create superusers
✔ Normalize email addresses
✔ Hash passwords
✔ Validate required fields

-------------------------------------------------------------------------------

IMPORTANT

Business logic such as:

❌ Login
❌ JWT
❌ Email verification
❌ OTP
❌ AI

does NOT belong here.

Only user creation belongs here.

===============================================================================
"""

# =============================================================================
# Django Imports
# =============================================================================

# BaseUserManager provides helper methods used to build a custom user manager.
from django.contrib.auth.base_user import BaseUserManager


# =============================================================================
# User Manager
# =============================================================================

class UserManager(BaseUserManager):
    """
    Custom manager used by the ChatDen User model.

    Every user account in ChatDen should be created through this manager.

    Advantages:

    • Centralized user creation
    • Password hashing
    • Email normalization
    • Consistent account creation
    • Easier future maintenance
    """

    # Allows this manager to be serialized during Django migrations.
    use_in_migrations = True

    # -------------------------------------------------------------------------
    # Create Regular User
    # -------------------------------------------------------------------------

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user.

        Parameters
        ----------
        email
            User's email address.

        password
            Plain-text password supplied by the user.

        extra_fields
            Additional fields passed to the User model.

        Returns
        -------
        User
            Newly created user instance.
        """

        # ---------------------------------------------------------------------
        # Validate Email
        # ---------------------------------------------------------------------

        # Every ChatDen account must have an email.
        if not email:
            raise ValueError("Email address is required.")

        # ---------------------------------------------------------------------
        # Normalize Email
        # ---------------------------------------------------------------------

        # Converts addresses into Django's normalized format.
        #
        # Example:
        #
        # John@Example.COM
        #
        # becomes
        #
        # John@example.com
        #
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        email = self.normalize_email(email).lower()

        # ---------------------------------------------------------------------
        # Create User Instance
        # ---------------------------------------------------------------------

        # Build the model instance.
        #
        # At this stage the object exists only in memory.
        #
        user = self.model(
            email=email,
            **extra_fields,
        )

        # ---------------------------------------------------------------------
        # Password Hashing
        # ---------------------------------------------------------------------

        # Never save plain-text passwords.
        #
        # set_password()
        #
        # hashes the password securely before storing it.
        #
        user.set_password(password)

        # ---------------------------------------------------------------------
        # Save User
        # ---------------------------------------------------------------------

        # Persist the user in the configured database.
        #
        # self._db allows Django to support multiple databases in the future.
        #
        user.save(using=self._db)

        # Return the created user instance.
        return user

    # -------------------------------------------------------------------------
    # Create Superuser
    # -------------------------------------------------------------------------

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a Django superuser.

        Superusers have unrestricted administrative access.
        """

        # Ensure required permissions are enabled.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Safety validation.

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        # Delegate actual creation to create_user().
        #
        # This guarantees:
        #
        # ✔ Password hashing
        # ✔ Email normalization
        # ✔ Single source of truth
        #
        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )