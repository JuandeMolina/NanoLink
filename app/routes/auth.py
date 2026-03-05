"""
Module Name: Auth Blueprint
Description: Register, login and logout routes
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT

Extra details:
    GET method: shows form (register or login)
    POST method: handles user input from the form
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required

from ..core import db
from ..models import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        if not username or not email or not password:
            return jsonify({"error": "missing_fields"}), 400

        if password != password_confirm:
            return jsonify({"error": "passwords_mismatch"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "username_exists"}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "email_exists"}), 409

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)  # Hash password

        try:
            db.session.add(user)
            db.session.commit()

            # Login user automatically when created
            login_user(user)
            
            return redirect(url_for("main.index"))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "registration_failed"}), 500

    return render_template("register.html")

# Login route for existing users
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            return jsonify({"error": "missing_fields"}), 400

        # Search for user by username
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "invalid_credentials"}), 401

        # Auth user and create session
        login_user(user, remember=True)  # remember=True keeps the user logged in across sessions
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required  # If not logged in, redirects to login page
def logout():
    """
    Ruta para cerrar sesi\u00f3n del usuario.
    """
    logout_user()
    return redirect(url_for("main.index"))
