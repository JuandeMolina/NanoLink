"""
Module Name: Core Configuration
Description: This module creates the app and configures extensions for the Flask app.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import os
import logging
from pathlib import Path

from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()


def create_app(config_class=None):
    """Application factory pattern."""
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "app" / "templates"),
        static_folder=str(BASE_DIR / "app" / "static"),
    )

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        import config

        app.config.from_object(config.Config)

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore
    setup_logging(app)

    # Register blueprints
    from ..routes.main import main
    from ..routes.auth import auth
    from ..routes.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")

    # Register error handlers
    from ..errors import register_error_handlers

    register_error_handlers(app)

    # User loader — llamada HTTP al api (pendiente de implementar)
    @login_manager.user_loader
    def load_user(user_id):
        from flask import session
        import requests
        from ..models import User

        token = session.get("jwt")
        if not token:
            return None

        try:
            r = requests.get(
                "http://localhost:5001/api/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            if r.status_code != 200:
                return None
            return User.from_dict(r.json())
        except requests.RequestException:
            return None

    return app


def setup_logging(app):
    if not app.debug:
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "client.log"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
