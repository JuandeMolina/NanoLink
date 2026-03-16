"""
Module Name: Admin Blueprint
Description: Routes for users with admin privileges
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from datetime import datetime

from flask import Blueprint, render_template, jsonify, session, abort, url_for, redirect
from flask_login import current_user, logout_user

from ..utils import admin_required, api_delete, api_get, api_post, API_BASE, _handle_401

admin = Blueprint("admin", __name__)


@admin.route("/")
@admin_required
def index():
    r, status = api_get(f"{API_BASE}/admin")

    if status == 401:
        return redirect(url_for("auth.login"))
    if status == 429:
        abort(429)
    if status == 503 or r is None:
        abort(503)

    data = r.json() if status == 200 else {}
    for url in data.get("urls", []):
        url["created_at"] = datetime.fromisoformat(url["created_at"])

    return render_template(
        "admin.html",
        users=data.get("users", []),
        urls=data.get("urls", []),
        stats=data.get("stats", {}),
    )


@admin.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "self_demotion"}), 400

    r, status = api_post(f"{API_BASE}/admin/users/{user_id}/toggle-admin")

    if r is None:
        return jsonify({"error": "api_unavailable"}), 503
    return jsonify(r.json()), status


@admin.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "self_delete"}), 400

    r, status = api_delete(f"{API_BASE}/admin/users/{user_id}")

    if r is None:
        return jsonify({"error": "api_unavailable"}), 503
    return jsonify(r.json()), status


@admin.route("/urls/<int:url_id>", methods=["DELETE"])
@admin_required
def delete_url(url_id):
    r, status = api_delete(f"{API_BASE}/admin/urls/{url_id}")

    if r is None:
        return jsonify({"error": "api_unavailable"}), 503
    return jsonify(r.json()), status
