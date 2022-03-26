import asyncio

import httpx
import structlog

from .config import Configuration
from .handlers.external import status_data

PUBLISH_INTERVAL = 60

logger = structlog.get_logger(__name__)


async def publish_status() -> None:
    client = httpx.AsyncClient()
    publish_url = Configuration().publish_url

    if not publish_url:
        logger.info("Not publishing status")
        return

    while True:
        try:
            data = await status_data()
            response = await client.put(publish_url, json=data)
            response.raise_for_status()
            logger.info(response)

        except Exception as e:
            logger.exception(e)
            logger.error(f"Caught {e} while trying to publish status")

        await asyncio.sleep(PUBLISH_INTERVAL)
