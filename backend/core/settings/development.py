"""
===============================================================================
File: development.py
Location: backend/core/settings/development.py
Project: ChatDen
===============================================================================

PURPOSE
-------
This file contains settings specific to the local development environment.

Instead of duplicating every Django setting, it imports everything from
base.py and overrides only the settings that should behave differently
during development.

-------------------------------------------------------------------------------

ARCHITECTURE

                   base.py
                      │
                      │
          ┌───────────┴───────────┐
          │                       │
development.py          production.py

base.py
    ↑
    ├── Common configuration shared by every environment
    │
development.py
    ↑
    ├── Local developer configuration
    │
production.py
    ↑
    ├── Production server configuration

-------------------------------------------------------------------------------

WHY SEPARATE SETTINGS?

Keeping development and production settings separate provides:

• Better security
• Cleaner configuration
• Easier deployments
• Reduced risk of accidentally deploying insecure settings

-------------------------------------------------------------------------------

CURRENT STATE

At the moment every configuration comes from base.py.

As ChatDen grows this file will override only development-specific options.

Examples (Future)

DEBUG = True

EMAIL_BACKEND = ...

LOGGING = ...

CORS = ...

===============================================================================
"""

# =============================================================================
# Import Base Settings
# =============================================================================

"""
Import every configuration from base.py.

This keeps all common settings centralized while allowing this file
to override only what is needed for local development.
"""

from .base import *