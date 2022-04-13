import asyncio
from collections import deque
from typing import Deque, Set

import structlog
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.api_client import ApiClient

from .nginx_parser import NginxLogParser, NginxRequestStatistics

NGINX_NAMESPACE = "ingress-nginx"

logger = structlog.get_logger(__name__)


total_stats: Deque[NginxRequestStatistics] = deque()
request_ids: Set[str] = set()

CACHE_SIZE = 1000000
RESTART_SECONDS = 60


async def tail_nginx_log() -> None:
    while True:
        try:
            config.load_incluster_config()
            v1_api = client.CoreV1Api(ApiClient())
            parser = NginxLogParser()

            resp = await v1_api.list_namespaced_pod(NGINX_NAMESPACE)
            resp = await v1_api.read_namespaced_pod_log(
                resp.items[0].metadata.name,
                NGINX_NAMESPACE,
                follow=True,
                _preload_content=False,
            )

            while True:
                line = await asyncio.wait_for(resp.content.readline(), 300)
                if not line:
                    logger.error("No line retrieved")
                    break
                else:
                    stats = parser.parse(line.decode("utf-8"))

                    if stats:
                        logger.debug(stats)

                        if len(total_stats) > CACHE_SIZE:
                            item = total_stats.popleft()
                            request_ids.remove(item.request_id)

                        if stats.request_id not in request_ids:
                            total_stats.append(stats)
                            request_ids.add(stats.request_id)
                        else:
                            # If the connection reading the logs gets reset,
                            # we want to go over all the previous lines, but
                            # not have any duplicates.
                            logger.debug(
                                f"Tossing duplicate line {stats.request_id}"
                            )
        except asyncio.TimeoutError:
            logger.info("Timeout occurred; restarting.")
        except Exception as e:
            logger.exception(e)
            logger.error(
                f"Caught {e}, restarting in {RESTART_SECONDS} seconds"
            )
            await asyncio.sleep(RESTART_SECONDS)
