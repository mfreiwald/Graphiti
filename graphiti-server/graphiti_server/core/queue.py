"""Episode queue management for per-group processing."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable

from graphiti_core.nodes import EpisodeType

from graphiti_server.models import ENTITY_TYPES

logger = logging.getLogger(__name__)


class EpisodeQueue:
    """Manages episode processing for a specific group_id."""

    def __init__(self, group_id: str):
        """Initialize episode queue for a group."""
        self.group_id = group_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: asyncio.Task | None = None
        self.is_running = False

    async def start_worker(self, process_fn: Callable):
        """Start the queue worker."""
        if self.is_running:
            return

        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker(process_fn))
        logger.info(f"Started episode queue worker for group_id: {self.group_id}")

    async def _worker(self, process_fn: Callable):
        """Process episodes from the queue sequentially."""
        try:
            while True:
                # Get the next episode processing function and optional future
                item = await self.queue.get()

                if isinstance(item, tuple):
                    episode_fn, future = item
                else:
                    episode_fn = item
                    future = None

                result = None
                error = None
                try:
                    result = await episode_fn()
                except Exception as e:
                    error = e
                    logger.error(
                        f"Error processing queued episode for group_id {self.group_id}: {str(e)}"
                    )
                finally:
                    # Set future result if provided
                    if future is not None:
                        if error:
                            future.set_exception(error)
                        else:
                            future.set_result(result)

                    self.queue.task_done()
        except asyncio.CancelledError:
            logger.info(f"Episode queue worker for group_id {self.group_id} was cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in queue worker for group_id {self.group_id}: {str(e)}")
        finally:
            self.is_running = False

    async def add_episode(
        self,
        client,
        name: str,
        episode_body: str,
        source: EpisodeType,
        source_description: str,
        uuid: str | None,
        use_custom_entities: bool,
        wait_for_result: bool = False,
    ):
        """Add an episode to the processing queue.

        Args:
            client: Graphiti client instance
            name: Episode name
            episode_body: Episode content
            source: Episode source type
            source_description: Description of the source
            uuid: Optional episode UUID
            use_custom_entities: Whether to use custom entity types
            wait_for_result: If True, waits for processing and returns the result

        Returns:
            If wait_for_result is False: Queue position (int)
            If wait_for_result is True: AddEpisodeResults from graphiti_core
        """

        async def process_episode():
            logger.info(f"Processing queued episode '{name}' for group_id: {self.group_id}")

            # Use custom entity types if enabled
            entity_types = ENTITY_TYPES if use_custom_entities else {}

            result = await client.add_episode(
                name=name,
                episode_body=episode_body,
                source=source,
                source_description=source_description,
                group_id=self.group_id,
                uuid=uuid,
                reference_time=datetime.now(timezone.utc),
                entity_types=entity_types,
            )
            logger.info(f"Episode '{name}' processed successfully")
            return result

        if wait_for_result:
            # Create a future to wait for the result
            future: asyncio.Future[Any] = asyncio.Future()
            await self.queue.put((process_episode, future))

            # Wait for the worker to process this episode and return the result
            return await future
        else:
            # Fire-and-forget: just add to queue
            await self.queue.put(process_episode)
            return self.queue.qsize()

    async def stop(self):
        """Stop the queue worker."""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        self.is_running = False


# Global registry of episode queues
_episode_queues: dict[str, EpisodeQueue] = {}


def get_episode_queue(group_id: str) -> EpisodeQueue:
    """Get or create an episode queue for a group_id."""
    if group_id not in _episode_queues:
        _episode_queues[group_id] = EpisodeQueue(group_id)
    return _episode_queues[group_id]


async def cleanup_all_queues():
    """Stop all episode queue workers."""
    for queue in _episode_queues.values():
        await queue.stop()
    _episode_queues.clear()
