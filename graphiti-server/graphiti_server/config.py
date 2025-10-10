"""Configuration management for Graphiti REST Server."""

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Default model names
DEFAULT_LLM_MODEL = "gpt-5-mini"
SMALL_LLM_MODEL = "gpt-5-nano"
DEFAULT_EMBEDDER_MODEL = "text-embedding-3-large"

# Semaphore limit for concurrent operations
SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT", 10))


class LLMConfig(BaseModel):
    """Configuration for LLM client."""

    api_key: str
    base_url: str | None = None
    model: str = DEFAULT_LLM_MODEL
    small_model: str = SMALL_LLM_MODEL
    temperature: float | None = 1.0

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create LLM configuration from environment variables."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        model = os.environ.get("MODEL_NAME", "").strip() or DEFAULT_LLM_MODEL
        small_model = os.environ.get("SMALL_MODEL_NAME", "").strip() or SMALL_LLM_MODEL

        # Set temperature to None if model contains "gpt-5"
        temperature: float | None = 1.0
        if "gpt-5" in model.lower():
            temperature = None
        else:
            temperature = float(os.environ.get("LLM_TEMPERATURE", "1.0"))

        return cls(
            api_key=api_key,
            base_url=os.environ.get("OPENAI_BASE_URL"),
            model=model,
            small_model=small_model,
            temperature=temperature,
        )


class EmbedderConfig(BaseModel):
    """Configuration for embedder client."""

    model: str = DEFAULT_EMBEDDER_MODEL
    api_key: str
    base_url: str | None = None

    @classmethod
    def from_env(cls) -> "EmbedderConfig":
        """Create embedder configuration from environment variables."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        model = os.environ.get("EMBEDDER_MODEL_NAME", "").strip() or DEFAULT_EMBEDDER_MODEL

        return cls(
            model=model,
            api_key=api_key,
            base_url=os.environ.get("OPENAI_EMBEDDER_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL"),
        )


class Neo4jConfig(BaseModel):
    """Configuration for Neo4j database connection."""

    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        """Create Neo4j configuration from environment variables."""
        return cls(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            user=os.environ.get("NEO4J_USER", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "password"),
        )


class ServerConfig(BaseModel):
    """Main server configuration."""

    llm: LLMConfig
    embedder: EmbedderConfig
    neo4j: Neo4jConfig
    default_group_id: str = "default"
    use_custom_entities: bool = False
    semaphore_limit: int = SEMAPHORE_LIMIT

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create server configuration from environment variables."""
        return cls(
            llm=LLMConfig.from_env(),
            embedder=EmbedderConfig.from_env(),
            neo4j=Neo4jConfig.from_env(),
        )


# Global config instance
_config: ServerConfig | None = None


def get_config() -> ServerConfig:
    """Get the global server configuration."""
    global _config
    if _config is None:
        _config = ServerConfig.from_env()
    return _config


def set_config(config: ServerConfig) -> None:
    """Set the global server configuration."""
    global _config
    _config = config
