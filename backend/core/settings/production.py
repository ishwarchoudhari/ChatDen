"""
===============================================================================
File: production.py
Location: backend/core/settings/production.py
Project: ChatDen
===============================================================================

PURPOSE
-------
This file contains settings used when ChatDen is deployed to a production
environment.

It imports the shared configuration from base.py and overrides only the
settings that should differ in production.

-------------------------------------------------------------------------------

WHY A SEPARATE PRODUCTION FILE?

Production environments require additional security and operational
configuration that should never be enabled during local development.

Examples include:

• DEBUG = False
• Secure Cookies
• HTTPS enforcement
• HSTS
• Secure Proxy Headers
• Production Logging
• Email Backend
• Static File Storage
• Media Storage
• Redis
• Caching

Keeping these settings isolated reduces the risk of accidentally running
a production server with development options.

-------------------------------------------------------------------------------

CURRENT STATE

At the moment, this file inherits all configuration from base.py.

Production-specific overrides will be added later in the roadmap as we
prepare the application for deployment.

===============================================================================
"""

# =============================================================================
# Import Base Settings
# =============================================================================

"""
Import all common configuration shared across every environment.

Production-specific settings will override values from base.py as needed.
"""

from .base import *