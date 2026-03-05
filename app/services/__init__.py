"""Business logic services."""

import random
import string
from ..models import URL, db


class URLService:
    """Service for URL shortening operations."""

    @staticmethod
    def generate_alias(length=6):
        """Generate a unique alias for the URL."""
        alphabet = string.ascii_uppercase + string.digits
        while True:
            alias = ''.join(random.choice(alphabet) for _ in range(length))
            if not URL.query.filter_by(alias=alias).first():
                return alias

    @staticmethod
    def create_short_url(original_url, user_id=None):
        """Create a new short URL."""
        alias = URLService.generate_alias()
        url = URL(alias=alias, original_url=original_url, user_id=user_id)
        db.session.add(url)
        db.session.commit()
        return url

    @staticmethod
    def get_url_by_alias(alias):
        """Retrieve URL by alias."""
        return URL.query.filter_by(alias=alias).first()

    @staticmethod
    def delete_url(url_id, user_id):
        """Delete URL if owned by user."""
        url = URL.query.get(url_id)
        if url and url.user_id == user_id:
            db.session.delete(url)
            db.session.commit()
            return True
        return False