"""
Module Name: Admin Namespace
Description: Admin endpoints for user and URL management
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from ..core import db
from ..models import User, URL

ns = Namespace("admin", description="Admin operations", path="/api/admin")

# ── Models ────────────────────────────────────────────────────────────────────

stats_output = ns.model(
    "StatsOutput",
    {
        "total_users": fields.Integer,
        "total_admins": fields.Integer,
        "total_urls": fields.Integer,
        "anonymous_urls": fields.Integer,
    },
)

user_item = ns.model(
    "AdminUserItem",
    {
        "id": fields.Integer,
        "username": fields.String,
        "email": fields.String,
        "is_admin": fields.Boolean,
        "is_superadmin": fields.Boolean,
    },
)

url_item = ns.model(
    "AdminURLItem",
    {
        "id": fields.Integer,
        "alias": fields.String,
        "original_url": fields.String,
        "user_id": fields.Integer,
        "created_at": fields.String,
    },
)

admin_data_output = ns.model(
    "AdminDataOutput",
    {
        "stats": fields.Nested(stats_output),
        "users": fields.List(fields.Nested(user_item)),
        "urls": fields.List(fields.Nested(url_item)),
    },
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _require_admin():
    """Verifica que el usuario autenticado es admin. Aborta con 403 si no."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or not user.is_admin:
        ns.abort(403, "admin_required")
    return user


# ── Resources ─────────────────────────────────────────────────────────────────


@ns.route("")
class AdminDashboard(Resource):

    @ns.doc(security="Bearer")
    @ns.marshal_with(admin_data_output)
    @jwt_required()
    def get(self):
        """Get global stats, all users and all URLs."""
        _require_admin()

        users = User.query.order_by(User.id).all()  # type: ignore[union-attr]
        urls = URL.query.order_by(URL.created_at.desc()).all()

        return {
            "stats": {
                "total_users": len(users),
                "total_admins": sum(1 for u in users if u.is_admin),
                "total_urls": len(urls),
                "anonymous_urls": sum(1 for u in urls if u.user_id is None),
            },
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "is_admin": u.is_admin,
                    "is_superadmin": u.is_superadmin,
                }
                for u in users
            ],
            "urls": [
                {
                    "id": u.id,
                    "alias": u.alias,
                    "original_url": u.original_url,
                    "user_id": u.user_id,
                    "created_at": u.created_at.isoformat(),
                }
                for u in urls
            ],
        }, 200


@ns.route("/users/<int:user_id>/toggle-admin")
class ToggleAdmin(Resource):

    @ns.doc(security="Bearer")
    @jwt_required()
    def post(self, user_id):
        """Toggle admin role for a user."""
        current = _require_admin()

        if current.id == user_id:  # type: ignore
            ns.abort(400, "self_demotion")

        user = User.query.get(user_id)
        if not user:
            ns.abort(404, "user_not_found")
        assert user is not None
        if user.is_superadmin:
            ns.abort(403, "superadmin_protected")

        try:
            user.is_admin = not user.is_admin  # type: ignore
            db.session.commit()
            return {"success": True, "is_admin": user.is_admin}, 200  # type: ignore
        except SQLAlchemyError:
            db.session.rollback()
            ns.abort(500, "db_error")


@ns.route("/users/<int:user_id>")
class AdminUserDetail(Resource):

    @ns.doc(security="Bearer")
    @jwt_required()
    def delete(self, user_id):
        """Delete a user and all their URLs."""
        current = _require_admin()

        if current.id == user_id:  # type: ignore
            ns.abort(400, "self_delete")

        user = User.query.get(user_id)
        if not user:
            ns.abort(404, "user_not_found")
        assert user is not None
        if user.is_superadmin:
            ns.abort(403, "superadmin_protected")

        try:
            URL.query.filter_by(user_id=user.id).delete()  # type: ignore
            db.session.delete(user)
            db.session.commit()
            return {"success": True}, 200
        except SQLAlchemyError:
            db.session.rollback()
            ns.abort(500, "db_error")


@ns.route("/urls/<int:url_id>")
class AdminURLDetail(Resource):

    @ns.doc(security="Bearer")
    @jwt_required()
    def delete(self, url_id):
        """Delete any URL."""
        _require_admin()

        url = URL.query.get(url_id)
        if not url:
            ns.abort(404, "url_not_found")

        try:
            db.session.delete(url)
            db.session.commit()
            return {"success": True}, 200
        except SQLAlchemyError:
            db.session.rollback()
            ns.abort(500, "db_error")
