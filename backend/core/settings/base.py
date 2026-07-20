"""
===============================================================================
File: base.py
Location: backend/core/settings/base.py
Project: ChatDen
===============================================================================

PURPOSE
-------
This is the main configuration file for the entire ChatDen backend.

Every Django environment (Development, Testing, Production)
inherits from this file.

Current hierarchy:

                base.py
                   │
          ┌────────┴────────┐
          │                 │
development.py      production.py

Everything common to every environment belongs here.

-------------------------------------------------------------------------------

RESPONSIBILITIES
----------------

• Configure Django
• Configure Installed Apps
• Configure Middleware
• Configure Templates
• Configure Database
• Configure Authentication
• Configure REST Framework
• Configure Static Files
• Configure Timezone
• Configure Security Defaults

-------------------------------------------------------------------------------

IMPORTANT

This file should NOT contain:

❌ Business Logic
❌ Database Queries
❌ API Logic
❌ Authentication Logic
❌ AI Logic

Only configuration belongs here.

===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

# Pathlib provides an object-oriented way of working with file system paths.
from pathlib import Path

# django-environ is used to securely read values from the .env file.
import environ

from datetime import timedelta


# =============================================================================
# Project Root Directory
# =============================================================================

"""
BASE_DIR points to the backend root directory.

Current structure:

backend/
│
├── manage.py
├── requirements.txt
├── .env
├── accounts/
├── core/
└── ...

Using BASE_DIR allows us to build paths that work on every operating system.
"""

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# Environment Variables
# =============================================================================

"""
Create an environment reader.

Instead of hardcoding secrets like:

SECRET_KEY = "..."

we read them from:

backend/.env

This is a security best practice.
"""

env = environ.Env()

"""
Load all environment variables from:

backend/.env

Example:

SECRET_KEY=...
DB_NAME=...
DB_USER=...
"""

environ.Env.read_env(BASE_DIR / ".env")


# =============================================================================
# Security
# =============================================================================

"""
SECRET_KEY

This key is used internally by Django for:

• Session signing
• CSRF protection
• Password reset tokens
• Cryptographic signing

Never commit the real value to GitHub.
"""

SECRET_KEY = env("SECRET_KEY")


"""
DEBUG

True  → Development

False → Production

Never deploy with DEBUG=True.
"""

DEBUG = env.bool("DEBUG", default=True)


"""
ALLOWED_HOSTS

Defines which hostnames can access Django.

Example for production:

[
    "chatden.com",
    "www.chatden.com",
]

Empty list is acceptable during local development.
"""

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"],
)


# =============================================================================
# Installed Applications
# =============================================================================

"""
INSTALLED_APPS

These are the applications loaded when Django starts.

Load order matters.

Current groups:

1. Django Core Apps
2. Local Apps
3. Third-party Apps
"""
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [

    # -------------------------------------------------------------------------
    # Django Built-in Applications
    # -------------------------------------------------------------------------

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authentication",
    "profiles",
    "relationships",
    "chat.apps.ChatConfig",

    # -------------------------------------------------------------------------
    # Local Applications
    # -------------------------------------------------------------------------

    "accounts",

    # -------------------------------------------------------------------------
    # Third-party Applications
    # -------------------------------------------------------------------------

    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
]


# =============================================================================
# Middleware
# =============================================================================

"""
Middleware runs on every request and response.

Request

↓

Security

↓

Session

↓

Common

↓

CSRF

↓

Authentication

↓

Messages

↓

Clickjacking

↓

Response
"""

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


# =============================================================================
# URL Configuration
# =============================================================================

"""
Entry point for every URL.

All URLs eventually begin here.
"""

ROOT_URLCONF = "core.urls"


# =============================================================================
# Templates
# =============================================================================

"""
Template configuration.

Currently used only by Django Admin.

Later the frontend will be Next.js,
so Django templates will have minimal usage.
"""

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

            ],
        },
    },
]


# =============================================================================
# WSGI
# =============================================================================

"""
WSGI entry point.

Used by traditional synchronous deployments.

Our production deployment will primarily use ASGI,
but WSGI remains available.
"""

WSGI_APPLICATION = "core.wsgi.application"


# =============================================================================
# Database
# =============================================================================

"""
ChatDen uses PostgreSQL.

Credentials are loaded securely from .env.
"""

DATABASES = {

    "default": {

        "ENGINE": "django.db.backends.postgresql",

        "NAME": env("DB_NAME"),

        "USER": env("DB_USER"),

        "PASSWORD": env("DB_PASSWORD"),

        "HOST": env("DB_HOST"),

        "PORT": env("DB_PORT"),

    }
}


# =============================================================================
# Password Validation
# =============================================================================

"""
Built-in Django password validators.

Additional custom password policies
will be added later.
"""

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },

]


# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =============================================================================
# Static Files
# =============================================================================

"""
Static files include:

• CSS
• JavaScript
• Images

During production these will later be served
through a dedicated static file solution.
"""

STATIC_URL = "static/"


# =============================================================================
# Custom User Model
# =============================================================================

"""
Tell Django to use our custom User model.

This MUST be defined before the first migration
of a production project.
"""

AUTH_USER_MODEL = "accounts.User"


# =============================================================================
# Django REST Framework
# =============================================================================

"""
Global DRF configuration.

JWT authentication,
permissions,
pagination,
renderers,
etc.

will be configured incrementally as we progress
through the roadmap.
"""

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "5/min",
        "user": "60/min",
    },
    # ... existing keys unchanged
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
    minutes=env.int("ACCESS_TOKEN_LIFETIME", default=15),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
    days=env.int("REFRESH_TOKEN_LIFETIME", default=7),
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "AUTH_TOKEN_CLASSES": (
        "rest_framework_simplejwt.tokens.AccessToken",
    ),
}