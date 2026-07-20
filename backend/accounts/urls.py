"""
===============================================================================
File: urls.py
Location: backend/accounts/urls.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Defines all HTTP endpoints exposed by the Accounts application.

This module maps incoming URLs to their corresponding View classes.

It acts as the public entry point for everything related to
authentication and account management.

-------------------------------------------------------------------------------

REQUEST FLOW

Client

    │

    ▼

core/urls.py

    │

    ▼

accounts/urls.py

    │

    ▼

Views

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

CURRENT ENDPOINTS

GET

/api/accounts/health/

Purpose

• Verify Accounts API is running.

------------------------------------------------------------

POST

/api/accounts/register/

Purpose

• Register a new ChatDen user.

-------------------------------------------------------------------------------

IMPORTANT

This file should ONLY contain routing.

Never place:

❌ Business Logic
❌ Authentication Logic
❌ Database Queries
❌ AI Logic
❌ Validation

Routing only.

===============================================================================
"""

# =============================================================================
# Django Imports
# =============================================================================

# Provides URL routing.
from django.urls import path


# =============================================================================
# Local Imports
# =============================================================================

# Import view classes exposed by this application.
from .views import (
    HealthCheckView,
    RegisterView,
)


# =============================================================================
# Accounts URL Configuration
# =============================================================================

"""
Every path defined here is automatically prefixed by:

/api/accounts/

because core/urls.py contains:

path(
    "api/accounts/",
    include("accounts.urls"),
)

Therefore:

path("register/")

becomes:

/api/accounts/register/
"""

urlpatterns = [

    # -------------------------------------------------------------------------
    # Health Check Endpoint
    # -------------------------------------------------------------------------
    #
    # URL
    #
    # GET /api/accounts/health/
    #
    # Used for:
    #
    # • Development
    # • Monitoring
    # • Deployment verification
    #
    path(
        "health/",
        HealthCheckView.as_view(),
        name="accounts-health",
    ),

    # -------------------------------------------------------------------------
    # User Registration Endpoint
    # -------------------------------------------------------------------------
    #
    # URL
    #
    # POST /api/accounts/register/
    #
    # Used to register new ChatDen users.
    #
    path(
        "register/",
        RegisterView.as_view(),
        name="accounts-register",
    ),
]