"""The main application factory for the sherlock service.

Notes
-----
Be aware that, following the normal pattern for FastAPI services, the app is
constructed when this module is loaded and is not deferred until a function is
called.
"""

import asyncio
from importlib.metadata import metadata, version

from fastapi import FastAPI
from safir.dependencies.http_client import http_client_dependency
from safir.logging import configure_logging
from safir.middleware.x_forwarded import XForwardedMiddleware

from .config import config
from .handlers.external import external_router
from .handlers.internal import internal_router
from .nginx_tailer import tail_nginx_log
from .publish_status import publish_status

__all__ = ["app", "config"]


configure_logging(
    profile=config.profile,
    log_level=config.log_level,
    name=config.logger_name,
)

app = FastAPI(
    title="sherlock",
    description=metadata("sherlock")["Summary"],
    version=version("sherlock"),
    openapi_url=f"/{config.name}/openapi.json",
    docs_url=f"/{config.name}/docs",
    redoc_url=f"/{config.name}/redoc",
)
"""The main FastAPI application for sherlock."""

# Attach the routers.
app.include_router(internal_router)
app.include_router(external_router, prefix=f"/{config.name}")

# Add the middleware.
app.add_middleware(XForwardedMiddleware)


@app.on_event("startup")
async def startup_event() -> None:
    asyncio.create_task(tail_nginx_log())
    asyncio.create_task(publish_status())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await http_client_dependency.aclose()
