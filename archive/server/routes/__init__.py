# Routes package
from .auth import bp as auth_bp
from .mesh import bp as mesh_bp
from .ai import bp as ai_bp

__all__ = ['auth_bp', 'mesh_bp', 'ai_bp']
