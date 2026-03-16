#!/usr/bin/env python3

"""
Module Name: Application Setup Script
Description:
    This module sets up the application, including
    database initialization and startup messages.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import sys
import socket
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core import create_app

API_ROOT = Path(__file__).resolve().parent.parent.parent
VENV_FLASK = API_ROOT.parent / "venv" / "bin" / "flask"


def create_superuser(app):
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@nanolink.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")

    if not admin_password:
        print(
            "[superuser] ADMIN_PASSWORD no está definida en .env: "
            "se omite la creación del superusuario"
        )
        return

    with app.app_context():
        from app.models import User
        from app.core import db

        existing = User.query.filter_by(username=admin_username).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.session.commit()
                print(f"[superuser] <{admin_username}> ya existía. Ahora es admin.")
            else:
                print(f"[superuser] <{admin_username}> ya existe y es admin.")
            return

        admin = User(username=admin_username, email=admin_email, is_admin=True, is_superadmin=True)  # type: ignore
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"[superuser] Cuenta admin creada: <{admin_username}> ({admin_email})")


def setup_app():
    """Setup the application: initialize database if needed and print startup info."""
    db_path = API_ROOT / "data" / "app.db"

    if not db_path.exists():
        print("Base de datos no encontrada. Inicializando...")
        db_path.parent.mkdir(parents=True, exist_ok=True)

    app = create_app()

    with app.app_context():
        from flask_migrate import init, migrate, upgrade
        from app.core import db

        migrations_path = str(API_ROOT / "migrations")

        if not (API_ROOT / "migrations").exists():
            init(directory=migrations_path)
            migrate(directory=migrations_path, message="Initial migration")

        upgrade(directory=migrations_path)
        print("Base de datos inicializada.")

    create_superuser(app)

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"API disponible en: http://{local_ip}:5001")


if __name__ == "__main__":
    setup_app()
