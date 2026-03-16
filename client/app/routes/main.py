"""
Module Name: Main Blueprint
Description: Main routes for the application
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import requests

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    jsonify,
    abort,
    session,
    url_for,
)
from flask_login import current_user, login_required, logout_user

from ..utils import admin_required, api_get, api_post, api_delete, API_BASE


main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main.route("/api/shorten", methods=["POST"])
def api_shorten():
    data = request.get_json(silent=True) or request.form or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "missing_url"}), 400

    r, status = api_post(f"{API_BASE}/urls/shorten", {"url": url})

    if status == 429:
        return jsonify({"error": "too_many_requests"}), 429
    if status in (503, 401) or r is None:
        return jsonify({"error": "api_unavailable"}), 503

    alias = r.json().get("alias")
    short_url = request.host_url.rstrip("/") + "/" + alias
    return jsonify({"shortUrl": short_url, "alias": alias}), 201


@main.route("/<short_id>", methods=["GET"])
def redirect_short(short_id):
    if "." in short_id:
        abort(404)

    r, status = api_get(f"{API_BASE}/urls/redirect/{short_id}")

    if status == 503 or r is None:
        abort(503)
    if status == 404:
        abort(404)
    if status == 200:
        return redirect(r.json().get("original_url"))
    abort(404)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    r, status = api_get(f"{API_BASE}/urls")

    if status == 401:
        return redirect(url_for("auth.login"))
    if status == 429:
        return abort(429)
    if status == 503 or r is None:
        abort(503)

    urls = r.json() if status == 200 else []
    return render_template("dashboard.html", urls=urls)


@main.route("/api/urls", methods=["GET"])
@login_required
def get_user_urls():
    r, status = api_get(f"{API_BASE}/urls")

    if r is None:
        return jsonify({"error": "api_unavailable"}), 503
    return jsonify(r.json()), status


@main.route("/api/urls/<int:url_id>", methods=["DELETE"])
@login_required
def delete_user_url(url_id):
    r, status = api_delete(f"{API_BASE}/urls/{url_id}")

    if r is None:
        return jsonify({"error": "api_unavailable"}), 503
    return jsonify(r.json()), status
