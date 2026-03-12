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
import subprocess
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import create_app


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
                print(f"[superuser] <{admin_username}> ahora existe y es admin.")
            return

        admin = User(username=admin_username, email=admin_email, is_admin=True)  # type: ignore
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"[superuser] Cuenta admin creada: <{admin_username}> ({admin_email})")


def setup_app():
    """Setup the application: initialize database if needed and print startup info."""
    # Verificar y inicializar base de datos si no existe
    db_path = Path(__file__).parent.parent / "data" / "app.db"
    migrations_path = Path(__file__).parent.parent / "migrations"
    if not db_path.exists():
        print("Base de datos no encontrada. Inicializando...")
        # Crear directorio data si no existe
        db_path.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["FLASK_APP"] = "nanolink.py"
        cwd = Path(__file__).parent.parent
        flask_cmd = str(Path(__file__).parent.parent / "venv" / "bin" / "flask")
        if not migrations_path.exists():
            subprocess.run([flask_cmd, "db", "init"], env=env, cwd=cwd, check=True)
        subprocess.run(
            [flask_cmd, "db", "migrate", "-m", "Initial migration"],
            env=env,
            cwd=cwd,
            check=True,
        )
        subprocess.run([flask_cmd, "db", "upgrade"], env=env, cwd=cwd, check=True)
        print("Base de datos inicializada.")

    app = create_app()
    create_superuser(app)

    # Obtener la IP local
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Aplicación disponible en: http://{local_ip}:5000")


def init_db():
    """Legacy function for manual database initialization."""
    app = create_app()
    with app.app_context():
        from app.core import db

        db.create_all()
        print("Database initialized.")


if __name__ == "__main__":
    init_db()
