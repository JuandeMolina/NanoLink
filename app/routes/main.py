from flask import Blueprint, render_template, request, redirect, jsonify
from flask_login import current_user, login_required
from ..core import db
from ..models import URL
from ..services import URLService
from ..utils import validate_url, sanitize_url
import sqlalchemy

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main.route("/api/shorten", methods=["POST"])
def api_shorten():
    """
    Endpoint para acortar URLs.
    Crea un alias único y lo guarda en la BD asociado al usuario (si está autenticado)
    """
    data = request.get_json(silent=True) or request.form or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "missing_url"}), 400

    # Validación y sanitización
    url = sanitize_url(url)
    if not validate_url(url):
        return jsonify({"error": "invalid_url"}), 400

    # Crear URL corta usando el servicio
    user_id = current_user.id if current_user.is_authenticated else None
    try:
        new_url = URLService.create_short_url(url, user_id)
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "storage_error"}), 500

    short_url = request.host_url.rstrip("/") + "/" + new_url.alias
    return jsonify({"shortUrl": short_url, "alias": new_url.alias}), 201


@main.route("/<short_id>", methods=["GET"])
def redirect_short(short_id):
    target = URLService.get_url_by_alias(short_id)
    if not target:
        return "URL no encontrada", 404
    return redirect(target.original_url)


@main.route("/dashboard", methods=["GET"])
@login_required  # Solo accesible si el usuario está autenticado
def dashboard():
    """
    Panel de control del usuario: muestra sus URLs acortadas
    """
    # Obtener todas las URLs del usuario autenticado
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", urls=urls)


@main.route("/api/urls", methods=["GET"])
@login_required  # Solo accesible si el usuario está autenticado
def get_user_urls():
    """
    API endpoint para obtener las URLs del usuario autenticado en JSON
    """
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return (
        jsonify(
            [
                {
                    "alias": url.alias,
                    "original_url": url.original_url,
                    "created_at": url.created_at.isoformat(),
                }
                for url in urls
            ]
        ),
        200,
    )


@main.route("/api/urls/<int:url_id>", methods=["DELETE"])
@login_required
def delete_user_url(url_id):
    """
    Eliminar una URL perteneciente al usuario autenticado.
    Endpoint: DELETE /api/urls/<url_id>
    """
    try:
        success = URLService.delete_url(url_id, current_user.id)
        if not success:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"success": True}), 200
    except sqlalchemy.exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "delete_failed"}), 500