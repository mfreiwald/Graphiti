"""FastAPI application and lifespan management."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from graphiti_server.api.deps import set_graphiti_client
from graphiti_server.api.routes import admin_router, memory_router, search_router
from graphiti_server.config import get_config
from graphiti_server.core import GraphitiClient, cleanup_all_queues

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    # Startup
    logger.info("Starting Graphiti REST server...")

    config = get_config()

    # Initialize Graphiti client
    client = GraphitiClient(config)
    await client.initialize()
    set_graphiti_client(client)

    logger.info("Graphiti REST server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Graphiti REST server...")

    # Stop all episode queues
    await cleanup_all_queues()

    # Close Graphiti client
    await client.close()

    logger.info("Graphiti REST server shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Graphiti REST API",
        description="REST API for Graphiti - a temporally-aware knowledge graph for AI agents",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Include routers
    app.include_router(memory_router)
    app.include_router(search_router)
    app.include_router(admin_router)

    return app


# Create app instance
app = create_app()
