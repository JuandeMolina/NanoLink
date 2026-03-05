"""
Module Name: Initialization
Description: This module initializes the whole application.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""


# Import from core module
from .core import create_app as _create_app

# Re-export for backward compatibility
create_app = _create_app
