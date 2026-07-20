"""
===============================================================================
File: views.py
Location: backend/accounts/views.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Defines the HTTP API endpoints for the Accounts application.

Views receive HTTP requests, coordinate serializers and business logic,
and return HTTP responses.

Current endpoints:

• Health Check
• User Registration

-------------------------------------------------------------------------------

REQUEST FLOW

Client

    │

    ▼

URL Router

    │

    ▼

APIView

    │

    ▼

Serializer

    │

    ▼

UserManager

    │

    ▼

Database

-------------------------------------------------------------------------------

RESPONSIBILITIES

✔ Receive HTTP requests
✔ Call serializers
✔ Return HTTP responses

-------------------------------------------------------------------------------

IMPORTANT

Views should NOT contain:

❌ Database logic
❌ Password hashing
❌ Authentication logic
❌ JWT creation
❌ Email sending
❌ AI logic

Those responsibilities belong elsewhere.

===============================================================================
"""

# =============================================================================
# Django REST Framework Imports
# =============================================================================

# Generic API views.
from rest_framework import generics, status

# Standard API response object.
from rest_framework.response import Response

# Base APIView class.
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# =============================================================================
# Local Imports
# =============================================================================

from .serializers import RegisterSerializer
from rest_framework.throttling import AnonRateThrottle

# =============================================================================
# Health Check API
# =============================================================================

class HealthCheckView(APIView):
    """
    Simple endpoint used to verify that the Accounts API is reachable.

    This endpoint performs no authentication and does not access
    the database.

    Typical uses:

    • Development testing
    • Deployment verification
    • Monitoring
    """

    # Allow anonymous access.
    authentication_classes = []

    # No permissions required.
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Handle GET requests.

        Returns
        -------
        HTTP 200
            Indicates the Accounts API is running.
        """

        return Response(
            {
                "status": "success",
                "service": "accounts",
                "message": "Accounts API is running.",
            },
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Registration API
# =============================================================================

class RegisterView(generics.CreateAPIView):
    """
    Register a new ChatDen user.

    Workflow

    Client

        │

        ▼

    RegisterView

        │

        ▼

    RegisterSerializer

        │

        ▼

    UserManager

        │

        ▼

    Database
    """

    # Serializer responsible for validating registration data.
    serializer_class = RegisterSerializer

    # Registration is publicly accessible.
    authentication_classes = []
    
    # Registration requires no authentication.
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Create a new user account.

        Validation is delegated entirely to the serializer.

        Password hashing is delegated to UserManager.
        """

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            {
                "message": "User registered successfully."
            },
            status=status.HTTP_201_CREATED,
        )