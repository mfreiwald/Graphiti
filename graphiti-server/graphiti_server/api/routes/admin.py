"""Admin endpoints for status and maintenance."""

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from graphiti_core.utils.maintenance.graph_data_operations import clear_data

from graphiti_server.api.deps import get_graphiti_client
from graphiti_server.config import get_config
from graphiti_server.models import StatusResponse, SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])


@router.get("/healthcheck")
async def healthcheck():
    """Simple healthcheck for load balancers."""
    return JSONResponse(content={"status": "healthy"}, status_code=200)


@router.get("/api/v1/status", response_model=StatusResponse)
async def get_status():
    """Get server status and configuration."""
    try:
        client = get_graphiti_client()
        config = get_config()

        # Test database connection
        await client.client.driver.client.verify_connectivity()  # type: ignore

        return StatusResponse(
            status="ok",
            message="Graphiti REST server is running and connected to Neo4j",
            config={
                "model": config.llm.model,
                "small_model": config.llm.small_model,
                "temperature": config.llm.temperature,
                "default_group_id": config.default_group_id,
                "custom_entities_enabled": config.use_custom_entities,
                "semaphore_limit": config.semaphore_limit,
            },
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error checking Neo4j connection: {error_msg}")

        return StatusResponse(
            status="error",
            message=f"Graphiti REST server is running but Neo4j connection failed: {error_msg}",
        )


@router.post("/api/v1/clear", response_model=SuccessResponse)
async def clear_graph():
    """Clear all data from the graph and rebuild indices."""
    try:
        client = get_graphiti_client()

        await clear_data(client.client.driver)
        await client.client.build_indices_and_constraints()

        return SuccessResponse(message="Graph cleared successfully and indices rebuilt")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error clearing graph: {error_msg}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing graph: {error_msg}",
        )
