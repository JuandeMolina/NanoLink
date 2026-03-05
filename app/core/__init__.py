"""Core configuration and extensions for the Flask app."""

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=None):
    """Application factory pattern."""
    app = Flask(__name__)

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        import config
        app.config.from_object(config.Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Setup logging
    setup_logging(app)

    # Register blueprints
    from ..routes.main import main
    from ..routes.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")

    # Load user loader
    @login_manager.user_loader
    def load_user(user_id):
        from ..models import User
        return User.query.get(int(user_id))

    return app


def setup_logging(app):
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Add file handler if needed
    if not app.debug:
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)