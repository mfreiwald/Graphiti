"""API routes package."""

from graphiti_server.api.routes.memory import router as memory_router
from graphiti_server.api.routes.search import router as search_router
from graphiti_server.api.routes.admin import router as admin_router

__all__ = ["memory_router", "search_router", "admin_router"]
