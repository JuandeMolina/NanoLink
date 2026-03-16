"""
Module Name: Database User Model
Description:
    Database users table model.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from werkzeug.security import generate_password_hash, check_password_hash

from ..core import db


class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(128), nullable=False)
    is_admin: bool = db.Column(db.Boolean, default=False)
    is_superadmin: bool = db.Column(db.Boolean, default=False)

    urls = db.relationship(
        "URL", backref="owner", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
