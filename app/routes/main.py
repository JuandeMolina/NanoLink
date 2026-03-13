"""
Module Name: Main Blueprint
Description: Main routes for the application
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    jsonify,
    abort
)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from ..core import db
from ..models import URL
from ..services import URLService
from ..utils import validate_url, sanitize_url

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    

@main.route("/api/shorten", methods=["POST"])
def api_shorten():
    """
    URL endpoint for shortening URLS.
    Creates a new alias for the provided URL and saves it to the database if user is authenticated
    """
    data = request.get_json(silent=True) or request.form or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "missing_url"}), 400

    # Validation and sanitization
    url = sanitize_url(url)
    if not validate_url(url):
        return jsonify({"error": "invalid_url"}), 400

    # If the user is authenticated, associate the shortened URL with their account
    user_id = current_user.id if current_user.is_authenticated else None
    try:
        new_url = URLService.create_short_url(url, user_id)
    except SQLAlchemyError:
        db.session.rollback()
        abort(503)

    short_url = request.host_url.rstrip("/") + "/" + new_url.alias
    return jsonify({"shortUrl": short_url, "alias": new_url.alias}), 201


@main.route("/<short_id>", methods=["GET"])
def redirect_short(short_id):
    target = URLService.get_url_by_alias(short_id)
    if not target:
        abort(404)
    return redirect(target.original_url)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # Get all URLs created by user
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", urls=urls)


@main.route("/api/urls", methods=["GET"])
@login_required
def get_user_urls():
    """
    API endpoint to get all URLs created by the authenticated user in JSON format.
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
    Endpoint: DELETE /api/urls/<url_id>
    """
    try:
        success = URLService.delete_url(url_id, current_user.id)
        if not success:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"success": True}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "delete_failed"}), 500
