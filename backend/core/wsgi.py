"""
===============================================================================
File: wsgi.py
Location: backend/core/wsgi.py
Project: ChatDen
===============================================================================

PURPOSE
-------
This file is the WSGI (Web Server Gateway Interface) entry point
for the ChatDen backend.

It creates the WSGI application object used by traditional
synchronous web servers.

Although ChatDen will primarily use ASGI in production
(for WebSockets and real-time communication),
WSGI is still included because Django provides it by default and
some hosting providers or deployment environments may require it.

-------------------------------------------------------------------------------

WHAT IS WSGI?

WSGI is the traditional Python web interface.

Request

    │

    ▼

Gunicorn / Apache / IIS

    │

    ▼

WSGI

    │

    ▼

Django

-------------------------------------------------------------------------------

ASGI vs WSGI

WSGI

✔ Traditional HTTP
✔ Synchronous
✔ Suitable for standard websites

ASGI

✔ HTTP
✔ WebSockets
✔ Async Tasks
✔ AI Streaming
✔ Real-time Chat

ChatDen's production deployment will primarily use ASGI.

WSGI remains available for compatibility.

-------------------------------------------------------------------------------

CURRENT ROLE

Right now this file simply creates the Django WSGI application.

No business logic should ever be placed here.

===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

# Used to configure environment variables before Django starts.
import os


# =============================================================================
# Django Imports
# =============================================================================

# Creates the WSGI application object.
from django.core.wsgi import get_wsgi_application


# =============================================================================
# Configure Django Settings
# =============================================================================

"""
Tell Django which settings module should be loaded.

Current Environment:

Development

Production deployments will later use:

core.settings.production
"""

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings.development",
)


# =============================================================================
# Create WSGI Application
# =============================================================================

"""
Create the WSGI application.

Traditional web servers import this object when starting Django.

Examples:

• Gunicorn
• Apache mod_wsgi
• IIS (Windows)

ChatDen will primarily use ASGI,
but WSGI remains available for compatibility.
"""

application = get_wsgi_application()