import asyncio

import structlog
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.api_client import ApiClient

from .nginx_parser import NginxLogParser

NGINX_NAMESPACE = "ingress-nginx"

logger = structlog.get_logger(__name__)


total_stats = []

RESTART_SECONDS = 60


async def tail_nginx_log():
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
                line = await resp.content.readline()
                if not line:
                    logger.error("No line retrieved")
                    break
                else:
                    stats = parser.parse(line.decode("utf-8"))

                    if stats:
                        logger.info(stats)
                        total_stats.append(stats)
        except Exception as e:
            logger.exception(e)
            logger.error(
                f"Caught {e}, restarting in {RESTART_SECONDS} seconds"
            )
            await asyncio.sleep(RESTART_SECONDS)
