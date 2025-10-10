"""FastAPI dependencies."""

from graphiti_server.core import GraphitiClient

# Global client instance
_graphiti_client: GraphitiClient | None = None


def set_graphiti_client(client: GraphitiClient) -> None:
    """Set the global Graphiti client."""
    global _graphiti_client
    _graphiti_client = client


def get_graphiti_client() -> GraphitiClient:
    """Get the global Graphiti client."""
    if _graphiti_client is None:
        raise RuntimeError("Graphiti client not initialized")
    return _graphiti_client
