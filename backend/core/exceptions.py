"""
Global exception handling for the ChatDen REST API.

This module provides a single, centralized exception handler for all
Django REST Framework API views.

Responsibilities
----------------
- Return a consistent JSON error response format.
- Preserve the correct HTTP status codes.
- Preserve serializer validation details.
- Hide internal implementation details from API clients.
- Log unexpected server-side exceptions.

This module MUST NOT contain:
- Business logic
- Database queries
- Model operations
- Service calls
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


# Module-level logger.
# Uses Django's standard logging configuration.
logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.

    Workflow
    --------
    1. Let Django REST Framework handle all known exceptions.
    2. If DRF returns a response, convert it into our standard format.
    3. If DRF cannot handle the exception, log it and return a safe
       generic 500 response.
    """

    # Let DRF process known exceptions first.
    response = exception_handler(exc, context)

    # DRF handled the exception successfully.
    if response is not None:

        # Preserve field-level validation errors.
        detail = response.data

        # Build a consistent error payload.
        response.data = {
            "status": response.status_code,
            "error": exc.__class__.__name__,
            "detail": detail,
        }

        return response

    # ------------------------------------------------------------------
    # Unexpected exception
    # ------------------------------------------------------------------
    # This is likely a programming error or infrastructure problem.
    # Log the complete traceback for debugging while returning a generic
    # response to the client.
    logger.exception("Unhandled API exception")

    return Response(
        {
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "InternalServerError",
            "detail": "An unexpected error occurred.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )