"""
===============================================================================
File: urls.py
Location: backend/core/urls.py
Project: ChatDen
===============================================================================

PURPOSE
-------
This is the ROOT URL configuration for the entire ChatDen backend.

Every incoming HTTP request starts here.

This file does NOT contain business logic.

Instead, it acts like a traffic controller by forwarding incoming
requests to the appropriate Django application.

-------------------------------------------------------------------------------

REQUEST FLOW

Browser / Mobile App

        │

        ▼

core/urls.py

        │

        ├──────────────► admin/
        │
        │
        └──────────────► api/accounts/

-------------------------------------------------------------------------------

ARCHITECTURE

Client Request

        │

        ▼

core.urls

        │

        ▼

Application URLs

        │

        ▼

Views

        │

        ▼

Serializer

        │

        ▼

Database

-------------------------------------------------------------------------------

WHY KEEP THIS FILE SMALL?

A common beginner mistake is placing API logic directly in this file.

This file should ONLY define routing.

Business logic belongs inside:

accounts/
chat/
notifications/
chatbot/

===============================================================================
"""

# =============================================================================
# Django Imports
# =============================================================================

# Provides Django's built-in administration interface.
from django.contrib import admin

# Import URL routing utilities.
#
# path()
#     Defines URL patterns.
#
# include()
#     Delegates routing to another Django application.
#
from django.urls import include, path


# =============================================================================
# Root URL Patterns
# =============================================================================

"""
urlpatterns

This list defines every public entry point into the backend.

Each path delegates responsibility to another component.

Current Routes

/admin/
    Django Administration Panel

/api/accounts/
    Authentication & Account APIs

Future Routes

/api/chat/

/api/users/

/api/groups/

/api/notifications/

/api/chatbot/

/api/media/

"""

urlpatterns = [

    # -------------------------------------------------------------------------
    # Django Administration
    # -------------------------------------------------------------------------
    #
    # Built-in admin interface.
    #
    # Example:
    #
    # http://127.0.0.1:8000/admin/
    #
    path(
        "admin/",
        admin.site.urls),
    path(
        "api/v1/accounts/",
        include("accounts.urls")    
    ),
    path(
        "api/v1/authentication/",
        include("authentication.urls"),
        ),
    path(
        "api/v1/profiles/",
        include("profiles.urls"),
        ),    
    path(
        "api/v1/relationships/", 
        include("relationships.urls")
        ),
    path(
        "api/v1/chat/",
        include("chat.urls")
    ),    

    # -------------------------------------------------------------------------
    # Accounts API
    # -------------------------------------------------------------------------
    # Delegates every request beginning with:
    #
    # /api/v1/accounts/
    #
    # to:
    #
    # accounts/urls.py
    #
    # Example
    #
    # /api/accounts/register/
    #
    # becomes
    #
    # accounts.urls
    #
    
]