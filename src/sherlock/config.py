"""Configuration definition."""

from __future__ import annotations

import os
from dataclasses import dataclass

__all__ = ["Configuration", "config"]


@dataclass
class Configuration:
    """Configuration for sherlock."""

    name: str = os.getenv("SAFIR_NAME", "sherlock")
    """The application's name, which doubles as the root HTTP endpoint path.

    Set with the ``SAFIR_NAME`` environment variable.
    """

    profile: str = os.getenv("SAFIR_PROFILE", "development")
    """Application run profile: "development" or "production".

    Set with the ``SAFIR_PROFILE`` environment variable.
    """

    logger_name: str = os.getenv("SAFIR_LOGGER", "sherlock")
    """The root name of the application's logger.

    Set with the ``SAFIR_LOGGER`` environment variable.
    """

    log_level: str = os.getenv("SAFIR_LOG_LEVEL", "INFO")
    """The log level of the application's logger.

    Set with the ``SAFIR_LOG_LEVEL`` environment variable.
    """

    publish_url: str = os.getenv("PUBLISH_URL", "")
    """The url to publish the status to.

    This will allow for a dashboard to get updates
    pushed to it.
    """

    publish_key: str = os.getenv("PUBLISH_KEY", "")
    """The key to use for publishing the URL."""


config = Configuration()
"""Configuration for sherlock."""
