#!/usr/bin/env python3
"""CLI entry point for Graphiti REST Server."""

import argparse
import logging
import os
import sys

from graphiti_server.config import ServerConfig, set_config

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the Graphiti REST server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--host",
        default=os.environ.get("SERVER_HOST", "0.0.0.0"),
        help="Host to bind the server to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("SERVER_PORT", "8000")),
        help="Port to bind the server to",
    )
    parser.add_argument(
        "--group-id",
        default=os.environ.get("DEFAULT_GROUP_ID"),
        help="Default group ID for episodes",
    )
    parser.add_argument(
        "--use-custom-entities",
        action="store_true",
        help="Enable custom entity extraction (Preference, Procedure, Requirement)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    try:
        # Load configuration
        config = ServerConfig.from_env()

        # Apply CLI overrides
        if args.group_id:
            config.default_group_id = args.group_id
        if args.use_custom_entities:
            config.use_custom_entities = True

        # Set global config
        set_config(config)

        # Log configuration
        logger.info(f"Starting Graphiti REST server on {args.host}:{args.port}")
        logger.info(f"Default group_id: {config.default_group_id}")
        logger.info(f"Custom entities: {'enabled' if config.use_custom_entities else 'disabled'}")

        # Start server
        import uvicorn

        uvicorn.run(
            "graphiti_server.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )

    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
