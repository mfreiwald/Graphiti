"""Memory/episode management endpoints."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from graphiti_core.edges import EntityEdge
from graphiti_core.nodes import EpisodeType, EpisodicNode

from graphiti_server.api.deps import get_graphiti_client
from graphiti_server.config import get_config
from graphiti_server.core import get_episode_queue
from graphiti_server.models import AddMemoryRequest, AddMemoryResponse, SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["memory"])


@router.post("/memory", status_code=status.HTTP_202_ACCEPTED, response_model=SuccessResponse)
async def add_memory(request: AddMemoryRequest):
    """Add an episode to memory.

    This endpoint queues the episode for background processing and returns immediately.
    Episodes for the same group_id are processed sequentially to avoid race conditions.
    """
    try:
        client = get_graphiti_client()
        config = get_config()

        # Map string source to EpisodeType enum
        source_type = EpisodeType.text
        if request.source == "message":
            source_type = EpisodeType.message
        elif request.source == "json":
            source_type = EpisodeType.json

        # Use provided group_id or fall back to default
        group_id = request.group_id or config.default_group_id

        # Get or create episode queue for this group
        queue = get_episode_queue(group_id)

        # Start worker if not already running
        if not queue.is_running:
            await queue.start_worker(lambda: None)  # Worker function is in queue.add_episode

        # Add episode to queue
        position = await queue.add_episode(
            client=client.client,
            name=request.name,
            episode_body=request.episode_body,
            source=source_type,
            source_description=request.source_description,
            uuid=request.uuid,
            use_custom_entities=config.use_custom_entities,
        )

        return SuccessResponse(
            message=f"Episode '{request.name}' queued for processing (position: {position})"
        )

    except Exception as e:
        logger.error(f"Error queuing episode: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error queuing episode: {str(e)}",
        )


@router.post("/memory/sync", status_code=status.HTTP_201_CREATED, response_model=AddMemoryResponse)
async def add_memory_sync(request: AddMemoryRequest):
    """Add an episode to memory synchronously and return the episode UUID.

    This endpoint queues the episode for processing (maintaining correct order) and waits
    for completion before returning. Returns the episode UUID for tracking.

    Use this when you need the episode UUID immediately (e.g., for subsequent operations).
    For fire-and-forget operations with better throughput, use the async /memory endpoint.
    """
    try:
        client = get_graphiti_client()
        config = get_config()

        # Map string source to EpisodeType enum
        source_type = EpisodeType.text
        if request.source == "message":
            source_type = EpisodeType.message
        elif request.source == "json":
            source_type = EpisodeType.json

        # Use provided group_id or fall back to default
        group_id = request.group_id or config.default_group_id

        # Get or create episode queue for this group
        queue = get_episode_queue(group_id)

        # Start worker if not already running
        if not queue.is_running:
            await queue.start_worker(lambda: None)

        # Add episode to queue and WAIT for result
        result = await queue.add_episode(
            client=client.client,
            name=request.name,
            episode_body=request.episode_body,
            source=source_type,
            source_description=request.source_description,
            uuid=request.uuid,
            use_custom_entities=config.use_custom_entities,
            wait_for_result=True,  # This makes it synchronous
        )

        return AddMemoryResponse(
            message=f"Episode '{request.name}' processed successfully",
            episode_uuid=result.episode.uuid,
        )

    except Exception as e:
        logger.error(f"Error processing episode: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing episode: {str(e)}",
        )


@router.get("/episodes/{group_id}", response_model=list[dict])
async def get_episodes(group_id: str, last_n: int = 10):
    """Get the most recent episodes for a group."""
    try:
        client = get_graphiti_client()

        if last_n < 1 or last_n > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="last_n must be between 1 and 100",
            )

        episodes = await client.client.retrieve_episodes(
            group_ids=[group_id],
            last_n=last_n,
            reference_time=datetime.now(timezone.utc),
        )

        return [episode.model_dump(mode="json") for episode in episodes]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting episodes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting episodes: {str(e)}",
        )


@router.delete("/episode/{uuid}", response_model=SuccessResponse)
async def delete_episode(uuid: str):
    """Delete an episode by UUID."""
    try:
        client = get_graphiti_client()

        episodic_node = await EpisodicNode.get_by_uuid(client.client.driver, uuid)
        await episodic_node.delete(client.client.driver)

        return SuccessResponse(message=f"Episode with UUID {uuid} deleted successfully")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting episode: {error_msg}")

        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in error_msg.lower()
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        raise HTTPException(status_code=status_code, detail=f"Error deleting episode: {error_msg}")


@router.delete("/entity-edge/{uuid}", response_model=SuccessResponse)
async def delete_entity_edge(uuid: str):
    """Delete an entity edge by UUID."""
    try:
        client = get_graphiti_client()

        entity_edge = await EntityEdge.get_by_uuid(client.client.driver, uuid)
        await entity_edge.delete(client.client.driver)

        return SuccessResponse(message=f"Entity edge with UUID {uuid} deleted successfully")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting entity edge: {error_msg}")

        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in error_msg.lower()
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        raise HTTPException(
            status_code=status_code, detail=f"Error deleting entity edge: {error_msg}"
        )


@router.get("/entity-edge/{uuid}")
async def get_entity_edge(uuid: str):
    """Get an entity edge by UUID."""
    try:
        client = get_graphiti_client()

        entity_edge = await EntityEdge.get_by_uuid(client.client.driver, uuid)

        return client.format_fact_result(entity_edge)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error getting entity edge: {error_msg}")

        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in error_msg.lower()
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        raise HTTPException(
            status_code=status_code, detail=f"Error getting entity edge: {error_msg}"
        )
