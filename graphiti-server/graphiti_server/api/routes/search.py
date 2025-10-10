"""Search endpoints for nodes and facts."""

import logging

from fastapi import APIRouter, HTTPException, Query, status
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_RRF,
)
from graphiti_core.search.search_filters import SearchFilters

from graphiti_server.api.deps import get_graphiti_client
from graphiti_server.config import get_config
from graphiti_server.models import FactSearchResponse, NodeResult, NodeSearchResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/nodes", response_model=NodeSearchResponse)
async def search_nodes(
    query: str = Query(..., description="The search query"),
    group_ids: list[str] | None = Query(None, description="Optional list of group IDs to filter"),
    max_nodes: int = Query(10, ge=1, le=100, description="Maximum number of nodes to return"),
    center_node_uuid: str | None = Query(None, description="Optional UUID to center search around"),
    entity: str = Query("", description="Optional entity type filter (Preference, Procedure, Requirement)"),
):
    """Search for entity nodes with summaries."""
    try:
        client = get_graphiti_client()
        config = get_config()

        # Use provided group_ids or fall back to default
        effective_group_ids = group_ids if group_ids else ([config.default_group_id] if config.default_group_id else [])

        # Configure search
        if center_node_uuid:
            search_config = NODE_HYBRID_SEARCH_NODE_DISTANCE.model_copy(deep=True)
        else:
            search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        search_config.limit = max_nodes

        # Set up filters
        filters = SearchFilters()
        if entity:
            valid_entities = ["Preference", "Procedure", "Requirement"]
            if entity not in valid_entities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid entity type. Must be one of: {', '.join(valid_entities)}",
                )
            filters.node_labels = [entity]

        # Perform search
        search_results = await client.client._search(
            query=query,
            config=search_config,
            group_ids=effective_group_ids,
            center_node_uuid=center_node_uuid,
            search_filter=filters,
        )

        if not search_results.nodes:
            return NodeSearchResponse(message="No relevant nodes found", nodes=[])

        # Format results
        formatted_nodes = [
            NodeResult(
                uuid=node.uuid,
                name=node.name,
                summary=node.summary if hasattr(node, "summary") else "",
                labels=node.labels if hasattr(node, "labels") else [],
                group_id=node.group_id,
                created_at=node.created_at.isoformat(),
                attributes=node.attributes if hasattr(node, "attributes") else {},
            )
            for node in search_results.nodes
        ]

        return NodeSearchResponse(message="Nodes retrieved successfully", nodes=formatted_nodes)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching nodes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching nodes: {str(e)}",
        )


@router.get("/facts", response_model=FactSearchResponse)
async def search_facts(
    query: str = Query(..., description="The search query"),
    group_ids: list[str] | None = Query(None, description="Optional list of group IDs to filter"),
    max_facts: int = Query(10, ge=1, le=100, description="Maximum number of facts to return"),
    center_node_uuid: str | None = Query(None, description="Optional UUID to center search around"),
):
    """Search for facts (relationships between entities)."""
    try:
        client = get_graphiti_client()
        config = get_config()

        # Use provided group_ids or fall back to default
        effective_group_ids = group_ids if group_ids else ([config.default_group_id] if config.default_group_id else [])

        # Perform search
        relevant_edges = await client.client.search(
            group_ids=effective_group_ids,
            query=query,
            num_results=max_facts,
            center_node_uuid=center_node_uuid,
        )

        if not relevant_edges:
            return FactSearchResponse(message="No relevant facts found", facts=[])

        facts = [client.format_fact_result(edge) for edge in relevant_edges]

        return FactSearchResponse(message="Facts retrieved successfully", facts=facts)

    except Exception as e:
        logger.error(f"Error searching facts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching facts: {str(e)}",
        )
