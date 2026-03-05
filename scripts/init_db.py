#!/usr/bin/env python3

"""
Module Name: Database Initialization Script
Description: This module initializes the database for the application.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core import create_app, db

def init_db():
    """Initialize the database."""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized.")

if __name__ == "__main__":
    init_db()