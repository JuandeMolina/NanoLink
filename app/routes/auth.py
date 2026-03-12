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

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    jsonify
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from ..core import db
from ..models import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        username = (request.form.get("username") or "").strip()
        email    = (request.form.get("email")    or "").strip()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        # Validation errors: re-render the form with a message
        if not username or not email or not password:
            return render_template("register.html", error="Rellena todos los campos."), 400

        if password != password_confirm:
            return render_template("register.html", error="Las contraseñas no coinciden."), 400

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Ese nombre de usuario ya está en uso."), 409

        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Ese correo ya tiene una cuenta asociada."), 409

        # Create new user
        user = User(username=username, email=email) # type: ignore
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("main.index"))
        except Exception:
            db.session.rollback()
            abort(500)  # Triggers the 500 handler → renders error.html

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        # Validation error: re-render the form with a message
        if not username or not password:
            return render_template("login.html", error="Introduce tu usuario y contraseña."), 400

        user = User.query.filter_by(username=username).first()

        # Wrong credentials: re-render the form with a generic message
        # (deliberately vague: don't reveal whether the username exists)
        if not user or not user.check_password(password):
            return render_template("login.html", error="Usuario o contraseña incorrectos."), 401

        login_user(user, remember=True)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@auth.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """
    API endpoint para cambiar la contraseña del usuario autenticado.
    Consumido por fetch() desde dashboard.html.
    """
    data = request.get_json(silent=True) or {}
 
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""
 
    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "Rellena todos los campos."}), 400
 
    if not current_user.check_password(current_password):
        return jsonify({"error": "La contraseña actual es incorrecta."}), 401
 
    if new_password != confirm_password:
        return jsonify({"error": "Las contraseñas nuevas no coinciden."}), 400
 
    if len(new_password) < 8:
        return jsonify({"error": "La nueva contraseña debe tener al menos 8 caracteres."}), 400
 
    if current_password == new_password:
        return jsonify({"error": "La nueva contraseña debe ser distinta a la actual."}), 400
 
    try:
        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error al guardar la contraseña."}), 500