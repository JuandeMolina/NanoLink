"""
Module Name: Database Models
Description:
    This module defines the database models for the application,
    including the User and URL models.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .core import db


class User(UserMixin, db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(128), nullable=False)

    urls = db.relationship("URL", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class URL(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    alias: str = db.Column(db.String(6), unique=True, nullable=False, index=True)
    original_url: str = db.Column(db.Text, nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<URL {self.alias} -> {self.original_url}>"
