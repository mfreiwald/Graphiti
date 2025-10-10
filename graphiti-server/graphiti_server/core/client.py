"""Graphiti client wrapper."""

import logging
from typing import cast

from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client import LLMClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.embedder.client import EmbedderClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

from graphiti_server.config import ServerConfig
from graphiti_server.models import FactResult

logger = logging.getLogger(__name__)


class GraphitiClient:
    """Wrapper around Graphiti core client."""

    def __init__(self, config: ServerConfig):
        """Initialize Graphiti client with configuration."""
        self.config = config
        self._client: Graphiti | None = None

    async def initialize(self) -> None:
        """Initialize the Graphiti client and database."""
        # Create LLM client
        llm_client = self._create_llm_client()

        # Create embedder client
        embedder_client = self._create_embedder_client()

        # Initialize Graphiti client
        self._client = Graphiti(
            uri=self.config.neo4j.uri,
            user=self.config.neo4j.user,
            password=self.config.neo4j.password,
            llm_client=llm_client,
            embedder=embedder_client,
            max_coroutines=self.config.semaphore_limit,
        )

        # Build indices and constraints
        await self._client.build_indices_and_constraints()

        logger.info("Graphiti client initialized successfully")
        logger.info(f"Using OpenAI model: {self.config.llm.model}")
        logger.info(f"Using temperature: {self.config.llm.temperature}")
        logger.info(f"Default group_id: {self.config.default_group_id}")
        logger.info(
            f"Custom entity extraction: {'enabled' if self.config.use_custom_entities else 'disabled'}"
        )
        logger.info(f"Concurrency limit: {self.config.semaphore_limit}")

    async def close(self) -> None:
        """Close the Graphiti client."""
        if self._client:
            await self._client.close()

    def _create_llm_client(self) -> LLMClient:
        """Create an LLM client from configuration."""
        llm_config = LLMConfig(
            api_key=self.config.llm.api_key,
            base_url=self.config.llm.base_url,
            model=self.config.llm.model,
            small_model=self.config.llm.small_model,
            temperature=self.config.llm.temperature,
        )
        return OpenAIClient(config=llm_config)

    def _create_embedder_client(self) -> EmbedderClient:
        """Create an embedder client from configuration."""
        embedder_config = OpenAIEmbedderConfig(
            api_key=self.config.embedder.api_key,
            base_url=self.config.embedder.base_url,
            embedding_model=self.config.embedder.model,
        )
        return OpenAIEmbedder(config=embedder_config)

    @property
    def client(self) -> Graphiti:
        """Get the underlying Graphiti client."""
        if self._client is None:
            raise RuntimeError("Graphiti client not initialized. Call initialize() first.")
        return self._client

    @staticmethod
    def format_fact_result(edge: EntityEdge) -> FactResult:
        """Format an entity edge into a FactResult."""
        return FactResult(
            uuid=edge.uuid,
            name=edge.name,
            fact=edge.fact,
            valid_at=edge.valid_at,
            invalid_at=edge.invalid_at,
            created_at=edge.created_at,
            expired_at=edge.expired_at,
            source_node_uuid=edge.source_node_uuid,
            target_node_uuid=edge.target_node_uuid,
        )
