import asyncio

import httpx
import structlog

from .config import Configuration
from .handlers.external import status_data

PUBLISH_INTERVAL = 60

logger = structlog.get_logger(__name__)


async def publish_status() -> None:
    c = Configuration()
    client = httpx.AsyncClient()

    if not c.publish_url:
        logger.info("Not publishing status")
        return

    while True:
        try:
            data = await status_data()
            response = await client.put(
                c.publish_url,
                headers={"Authorization": f"digest {c.publish_key}"},
                json=data,
            )
            response.raise_for_status()
            logger.info(response)

        except Exception as e:
            logger.exception(e)
            logger.error(f"Caught {e} while trying to publish status")

        await asyncio.sleep(PUBLISH_INTERVAL)
