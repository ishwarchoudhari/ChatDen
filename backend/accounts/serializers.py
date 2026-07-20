"""
accounts/serializers.py

Serializers for the Accounts application.

Responsibilities:
- Validate incoming request data.
- Convert JSON ↔ Python objects.
- Delegate user creation to the UserManager.
"""
"""
===============================================================================
File: serializers.py
Location: backend/accounts/serializers.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Defines serializers for the Accounts application.

A serializer is responsible for converting incoming JSON data into Python
objects, validating that data, and preparing it for database operations.

It is the first security layer for incoming API requests.

-------------------------------------------------------------------------------

RESPONSIBILITIES

✔ Validate incoming request data
✔ Normalize user input
✔ Convert JSON → Python objects
✔ Delegate user creation to UserManager

-------------------------------------------------------------------------------

REQUEST FLOW

Client

    │

    ▼

RegisterView

    │

    ▼

RegisterSerializer

    │

    ▼

Validation

    │

    ▼

UserManager

    │

    ▼

Database

-------------------------------------------------------------------------------

IMPORTANT

Serializers should NEVER:

❌ Generate JWT
❌ Login users
❌ Send emails
❌ Send OTP
❌ Access external APIs
❌ Execute business workflows

Business workflows belong in dedicated service classes (when introduced).

===============================================================================
"""

#from attr import attrs
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer used for user registration.

    Validation Flow:

    Request
        ↓
    Email Validation
        ↓
    Username Validation
        ↓
    Password Validation
        ↓
    UserManager.create_user()
        ↓
    Database
    """

    # ------------------------------------------------------------------
    # Email Field
    # ------------------------------------------------------------------
    #
    # Disable DRF's automatic UniqueValidator because we want complete
    # control over validation messages and future business rules.
    #
    email = serializers.EmailField(
        validators=[],
    )

    # ------------------------------------------------------------------
    # Username Field
    # ------------------------------------------------------------------
    #
    # Same reason as email.
    #
    username = serializers.CharField(
        validators=[],
    )

    # ------------------------------------------------------------------
    # Password Field
    # ------------------------------------------------------------------
    #
    # Password is write_only so it never appears in API responses.
    #
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password_confirm",
        )

    # ------------------------------------------------------------------
    # Email Validation
    # ------------------------------------------------------------------

    def validate_email(self, value):
        """
        Normalize and validate email.
        """

        email = value.strip().lower()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return email

    # ------------------------------------------------------------------
    # Username Validation
    # ------------------------------------------------------------------

    def validate_username(self, value):
        """
        Validate username.
        """

        username = value.strip()

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Username is already taken."
            )

        return username

    # ------------------------------------------------------------------
    # Create User
    # ------------------------------------------------------------------

    def create(self, validated_data):
        """
        Delegate user creation to the custom UserManager.

        This guarantees:

        • Password hashing
        • Email normalization
        • Future compatibility with Google Login
        • Future compatibility with Phone OTP
        """
        validated_data.pop("password_confirm", None)  # Remove password_confirm before creating user
        return User.objects.create_user(**validated_data)
    
    def validate(self, attrs):
        """
        Perform object-level validation.

        A temporary User instance is created so Django's
        UserAttributeSimilarityValidator can compare the
        password against the supplied email and username.
        """
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                {
                    "password_confirm": [
                        "Passwords do not match."
                    ]
                }
            )
        user = User(
            email=attrs.get("email"),
            username=attrs.get("username"),
        )

        try:
            validate_password(
                password,
                user=user,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {
                    "password": list(exc.messages)
                }
            )

        return attrs
    