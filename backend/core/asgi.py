"""
===============================================================================
File: asgi.py
Location: backend/core/asgi.py
Project: ChatDen
===============================================================================

PURPOSE
-------
This file is the ASGI (Asynchronous Server Gateway Interface) entry point
for the ChatDen backend.

It is responsible for creating the ASGI application that modern servers
such as Uvicorn or Daphne execute.

Unlike WSGI, ASGI supports asynchronous communication.

This is one of the most important files because ChatDen will eventually
support:

• WebSockets
• Real-time Chat
• AI Streaming
• Notifications
• Presence
• Typing Indicators

-------------------------------------------------------------------------------

WHAT IS ASGI?

Traditional Django

Browser
    │
    ▼
WSGI
    │
    ▼
Django

Modern Django

Browser

HTTP

WebSocket

AI Stream

       │

       ▼

ASGI

       │

       ▼

Django

-------------------------------------------------------------------------------

WHY ASGI?

ChatDen is not a traditional website.

It is a real-time messaging platform.

That means users expect:

✔ Messages instantly
✔ Typing indicators instantly
✔ Online status instantly
✔ AI responses streamed instantly

Only ASGI supports this architecture.

-------------------------------------------------------------------------------

CURRENT STATE

Right now ASGI only serves HTTP requests.

Later this file will be extended with:

Channels

↓

Redis

↓

WebSocket Routing

↓

Authentication Middleware

↓

Consumers

===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

# Used for configuring environment variables before Django starts.
import os


# =============================================================================
# Django Imports
# =============================================================================

# Creates the ASGI application object used by ASGI servers.
from django.core.asgi import get_asgi_application


# =============================================================================
# Configure Django Settings
# =============================================================================

"""
Tell Django which settings module to use.

Current Environment:

Development

Later production servers will point to the production settings module.
"""

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings.development",
)


# =============================================================================
# Create ASGI Application
# =============================================================================

"""
Create the ASGI application.

Servers such as:

• Uvicorn
• Daphne
• Hypercorn

will import this variable.

Future Architecture

Uvicorn

↓

ASGI

↓

HTTP + WebSockets

↓

Django

↓

Chat

↓

Redis

↓

PostgreSQL
"""

application = get_asgi_application()