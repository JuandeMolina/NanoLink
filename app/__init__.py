# Import from core module
from .core import create_app as _create_app

# Re-export for backward compatibility
create_app = _create_app
