# Blueprint de autenticaci\u00f3n
# Rutas para registro, login y logout de usuarios

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required
from ..core import db
from ..models import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Ruta de registro de nuevos usuarios.
    GET: Muestra formulario de registro
    POST: Procesa el formulario y crea nuevo usuario
    """
    if request.method == "POST":
        # Obtener datos del formulario
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        # Validar que no haya campos vacios
        if not username or not email or not password:
            return jsonify({"error": "missing_fields"}), 400

        # Validar que las contrase\u00f1as coincidan
        if password != password_confirm:
            return jsonify({"error": "passwords_mismatch"}), 400

        # Validar que el usuario no exista ya
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "username_exists"}), 409

        # Validar que el email no exista ya
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "email_exists"}), 409

        # Crear nuevo usuario
        user = User(username=username, email=email)
        user.set_password(password)  # Hashear la contrase\u00f1a

        try:
            db.session.add(user)
            db.session.commit()
            # Autenticar al usuario autom\u00e1ticamente despu\u00e9s del registro
            login_user(user)
            return redirect(url_for("main.index"))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "registration_failed"}), 500

    # GET: mostrar formulario de registro
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Ruta de login de usuarios existentes.
    GET: Muestra formulario de login
    POST: Procesa credenciales y autentica al usuario
    """
    if request.method == "POST":
        # Obtener datos del formulario
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        # Validar que no haya campos vacios
        if not username or not password:
            return jsonify({"error": "missing_fields"}), 400

        # Buscar usuario por nombre de usuario
        user = User.query.filter_by(username=username).first()

        # Validar que el usuario exista y la contrase\u00f1a sea correcta
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid_credentials"}), 401

        # Autenticar al usuario
        login_user(
            user, remember=True
        )  # remember=True mantiene sesión más tiempo
        return redirect(url_for("main.index"))

    # GET: mostrar formulario de login
    return render_template("login.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required  # Si el usuario no está autenticado, lo redirige al login
def logout():
    """
    Ruta para cerrar sesi\u00f3n del usuario.
    """
    logout_user()
    return redirect(url_for("main.index"))
