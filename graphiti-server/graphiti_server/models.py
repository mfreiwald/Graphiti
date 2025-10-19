"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ==================== Custom Entity Types ====================


class Requirement(BaseModel):
    """A Requirement represents a specific need, feature, or functionality."""

    project_name: str = Field(
        ..., description="The name of the project to which the requirement belongs."
    )
    description: str = Field(
        ...,
        description="Description of the requirement. Only use information mentioned in the context.",
    )


class Preference(BaseModel):
    """A Preference represents a user's expressed like, dislike, or preference."""

    category: str = Field(..., description="The category of the preference (e.g., 'Brands', 'Food').")
    description: str = Field(
        ...,
        description="Brief description of the preference. Only use information mentioned in the context.",
    )


class Procedure(BaseModel):
    """A Procedure informing the agent what actions to take or how to perform in certain scenarios."""

    description: str = Field(
        ...,
        description="Brief description of the procedure. Only use information mentioned in the context.",
    )


ENTITY_TYPES: dict[str, BaseModel] = {
    "Requirement": Requirement,  # type: ignore
    "Preference": Preference,  # type: ignore
    "Procedure": Procedure,  # type: ignore
}


# ==================== Request Models ====================


class AddMemoryRequest(BaseModel):
    """Request model for adding an episode to memory."""

    name: str = Field(..., description="Name of the episode", max_length=200)
    episode_body: str = Field(
        ...,
        description='The content of the episode. When source="json", must be a valid JSON string.',
        min_length=1,
    )
    group_id: str | None = Field(
        None,
        description="A unique ID for this graph. If not provided, uses the default group_id from server config.",
    )
    source: Literal["text", "json", "message"] = Field(
        "text",
        description='Source type: "text" for plain text, "json" for structured data, "message" for conversations',
    )
    source_description: str = Field("", description="Description of the source")
    uuid: str | None = Field(None, description="Optional UUID for the episode")


# ==================== Response Models ====================


class SuccessResponse(BaseModel):
    """Generic success response."""

    message: str
    success: bool = True


class AddMemoryResponse(BaseModel):
    """Response model for add_memory endpoint."""

    message: str
    episode_uuid: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Generic error response."""

    error: str
    success: bool = False


class NodeResult(BaseModel):
    """Result model for a node."""

    uuid: str
    name: str
    summary: str
    labels: list[str]
    group_id: str
    created_at: str
    attributes: dict[str, Any]


class NodeSearchResponse(BaseModel):
    """Response model for node search."""

    message: str
    nodes: list[NodeResult]
    success: bool = True


class FactResult(BaseModel):
    """Result model for a fact (entity edge)."""

    uuid: str
    name: str
    fact: str
    valid_at: datetime | None
    invalid_at: datetime | None
    created_at: datetime
    expired_at: datetime | None
    source_node_uuid: str | None = None
    target_node_uuid: str | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.astimezone(datetime.now().astimezone().tzinfo).isoformat()}


class FactSearchResponse(BaseModel):
    """Response model for fact search."""

    message: str
    facts: list[FactResult]
    success: bool = True


class EpisodeSearchResponse(BaseModel):
    """Response model for episode search."""

    message: str
    episodes: list[dict[str, Any]]
    success: bool = True


class StatusResponse(BaseModel):
    """Response model for status endpoint."""

    status: Literal["ok", "error"]
    message: str
    config: dict[str, Any] | None = None
