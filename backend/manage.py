#!/usr/bin/env python
"""
===============================================================================
File: manage.py
Project: ChatDen
===============================================================================

Purpose
-------
This is Django's command-line entry point.

It acts as the central command dispatcher for all Django management commands.

Examples:
    python manage.py runserver
    python manage.py migrate
    python manage.py makemigrations
    python manage.py createsuperuser
    python manage.py collectstatic

-------------------------------------------------------------------------------

Responsibilities
----------------
• Configure Django before execution.
• Tell Django which settings file to load.
• Execute management commands entered from the terminal.

-------------------------------------------------------------------------------

Execution Flow
--------------

User runs

    python manage.py <command>

            │

            ▼

Set DJANGO_SETTINGS_MODULE

            │

            ▼

Load Django Framework

            │

            ▼

Execute Requested Command

-------------------------------------------------------------------------------

This file should remain extremely small.

Business logic, application logic, authentication, APIs,
database queries, etc. should NEVER be placed here.

===============================================================================
"""

# -----------------------------------------------------------------------------
# Standard Library Imports
# -----------------------------------------------------------------------------

# Used for interacting with environment variables.
import os

# Provides access to command-line arguments.
import sys


# -----------------------------------------------------------------------------
# Main Entry Function
# -----------------------------------------------------------------------------

def main():
    """
    Main entry point for every Django management command.

    This function performs three steps:

    1. Configure Django.
    2. Import Django's command executor.
    3. Execute the requested management command.

    This function is automatically executed when:

        python manage.py ...

    is run from the terminal.
    """

    # -------------------------------------------------------------------------
    # Configure Django Settings
    # -------------------------------------------------------------------------
    #
    # Django must know which settings module to use before it starts.
    #
    # Current Environment:
    #
    #     Development
    #
    # Later this may become:
    #
    #     core.settings.production
    #
    # during deployment.
    #
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "core.settings.development",
    )

    # -------------------------------------------------------------------------
    # Import Django Command Executor
    # -------------------------------------------------------------------------
    #
    # Importing is delayed until after the settings module is configured.
    #
    # Django depends on DJANGO_SETTINGS_MODULE being available before many
    # internal components can initialize correctly.
    #
    try:
        from django.core.management import execute_from_command_line

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------
    #
    # If Django cannot be imported, provide a helpful error message.
    #
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. "
            "Are you sure it's installed and available on your "
            "PYTHONPATH environment variable? "
            "Did you forget to activate a virtual environment?"
        ) from exc

    # -------------------------------------------------------------------------
    # Execute Command
    # -------------------------------------------------------------------------
    #
    # Executes the command entered by the developer.
    #
    # Examples:
    #
    #   python manage.py runserver
    #   python manage.py migrate
    #   python manage.py check
    #
    execute_from_command_line(sys.argv)


# -----------------------------------------------------------------------------
# Program Entry Point
# -----------------------------------------------------------------------------
#
# __name__ == "__main__"
#
# means this file was executed directly.
#
# It prevents main() from running if this file is imported by another module.
#
if __name__ == "__main__":
    main()