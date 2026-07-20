"""
===============================================================================
File: apps.py
Location: backend/accounts/apps.py
Project: ChatDen
===============================================================================

PURPOSE
-------
Defines the configuration for the Accounts application.

Every Django application contains one AppConfig class.

Django loads this configuration automatically during project startup.

-------------------------------------------------------------------------------

RESPONSIBILITIES

• Register the Accounts application.
• Provide application metadata.
• (Future) Register Django signals.
• (Future) Execute application startup tasks.

-------------------------------------------------------------------------------

APPLICATION STARTUP

When Django starts:

manage.py
    │
    ▼
Settings
    │
    ▼
INSTALLED_APPS
    │
    ▼
AccountsConfig
    │
    ▼
Accounts Application Ready

-------------------------------------------------------------------------------

IMPORTANT

Business logic should NEVER be placed here.

Database queries should NEVER be placed here.

Authentication should NEVER be placed here.

This class is responsible only for configuring the application.

===============================================================================
"""

# =============================================================================
# Django Imports
# =============================================================================

from django.apps import AppConfig


# =============================================================================
# Accounts Application Configuration
# =============================================================================

class AccountsConfig(AppConfig):
    """
    Configuration class for the Accounts application.

    Django creates one instance of this class when the
    application is loaded during startup.
    """

    # Name of the Django application.
    # This must match the application directory.
    name = "accounts"