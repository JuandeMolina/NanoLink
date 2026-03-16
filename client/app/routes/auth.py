"""
Module Name: Auth Blueprint
Description: Register, login and logout routes
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    abort,
)
from flask_login import login_user, logout_user, login_required

from ..models import User
from ..utils import api_post, API_BASE

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            return (
                render_template(
                    "login.html", error="Introduce tu usuario y contraseña."
                ),
                400,
            )

        r, status = api_post(
            f"{API_BASE}/users/login",
            {"username": username, "password": password},
            handle_401=False,
        )

        if status == 429:
            abort(429)
        if status in (500, 503):
            abort(503)
        if status != 200:
            return (
                render_template(
                    "login.html", error="Usuario o contraseña incorrectos."
                ),
                401,
            )

        data = r.json()  # type: ignore
        session["jwt"] = data["access_token"]
        user = User.from_dict(data["user"])
        login_user(user, remember=True)
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        password_confirm = request.form.get("password_confirm") or ""

        if not username or not email or not password:
            return (
                render_template("register.html", error="Rellena todos los campos."),
                400,
            )

        if password != password_confirm:
            return (
                render_template("register.html", error="Las contraseñas no coinciden."),
                400,
            )

        r, status = api_post(
            f"{API_BASE}/users/register",
            {"username": username, "email": email, "password": password},
        )

        if status == 429:
            abort(429)
        if status in (500, 503):
            abort(503)
        if status == 409:
            data = r.json()  # type: ignore
            msg = (
                "Ese nombre de usuario ya está en uso."
                if "username" in data.get("message", "")
                else "Ese correo ya tiene una cuenta asociada."
            )
            return render_template("register.html", error=msg), 409
        if status != 201:
            abort(status)

        register_data = r.json()  # type: ignore

        # Login automático tras registro
        r_login, login_status = api_post(
            f"{API_BASE}/users/login", {"username": username, "password": password}
        )

        if login_status == 429:
            abort(429)
        if login_status in (500, 503) or r_login is None:
            abort(503)
        if login_status != 200:
            return redirect(url_for("auth.login"))

        login_data = r_login.json()
        session["jwt"] = login_data["access_token"]
        user = User.from_dict(register_data)
        login_user(user)
        return redirect(url_for("main.index"))

    return render_template("register.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.pop("jwt", None)
    logout_user()
    return redirect(url_for("main.index"))
