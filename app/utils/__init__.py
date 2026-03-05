"""
Module Name: Utility functions
Description:
    This module contains utility functions for URL validation and sanitization.
    These functions are used across the application to ensure that user input
    is properly validated and sanitized before being processed or stored.
Author: Juande Molina
Copyright: (c) 2026 JuandeMolina
License: MIT
"""

import re


def validate_url(url):
    """Basic URL validation."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None


def sanitize_url(url):
    """Basic URL sanitization."""
    return url.strip()