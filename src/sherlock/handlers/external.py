"""Handlers for the app's external root, ``/sherlock/``."""

import pandas as pd
from fastapi import APIRouter, Depends, Response
from safir.dependencies.logger import logger_dependency
from structlog.stdlib import BoundLogger

from ..nginx_tailer import total_stats

__all__ = ["get_all", "get_errors", "get_laggers", "external_router"]

external_router = APIRouter()
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    description=(
        "Get all the stats in memory in a JSON file that can be parsed"
    ),
    summary="All recent request statistics",
)
async def get_all(
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent transactions in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    return Response(content=df.to_html())


@external_router.get(
    "/errors",
    description=("Get all the requests that returned a 5xx"),
    summary="All recent 5xx requests",
)
async def get_errors(
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent errors in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    errors = df[df["status_code"] >= 500]
    return Response(content=errors.to_html())


@external_router.get(
    "/laggers",
    description=("Get all the recent requests that took a long time"),
    summary="All recent requests that took a long time",
)
async def get_laggers(
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent errors in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    laggers = df[df["request_time"] >= 10]
    return Response(content=laggers.to_html())
