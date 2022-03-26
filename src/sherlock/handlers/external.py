"""Handlers for the app's external root, ``/sherlock/``."""

import json
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Response
from safir.dependencies.logger import logger_dependency
from structlog.stdlib import BoundLogger

from ..nginx_tailer import total_stats

__all__ = [
    "get_all",
    "get_errors",
    "get_laggers",
    "get_services",
    "get_service_errors",
    "get_service_laggers",
    "get_service_stats",
    "get_status",
    "status_data",
    "external_router",
]

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
    return Response(content=df.to_json(orient="records"))


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
    return Response(content=errors.to_json(orient="records"))


@external_router.get(
    "/laggers",
    description=("Get all the recent requests that took a long time"),
    summary="All recent requests that took a long time",
)
async def get_laggers(
    time: int = 30,
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent errors in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    laggers = df[df["request_time"] >= time]
    return Response(content=laggers.to_json(orient="records"))


@external_router.get(
    "/service/",
    description=("All the services that have a request logged"),
    summary="All the services that have a request logged",
)
async def get_services(
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent services in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    services = df["service_name"].unique().tolist()
    return Response(content=json.dumps(services))


@external_router.get(
    "/service/{service_name}/",
    description=("All the requests for a service"),
    summary="All the requests for a service",
)
async def get_service_requests(
    service_name: str,
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent services in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    services = df["service_name"].unique().tolist()

    if service_name not in services:
        raise HTTPException(status_code=404, detail="Item not found")

    service_logs = df[df["service_name"] == service_name]
    return Response(content=service_logs.to_json(orient="records"))


@external_router.get(
    "/service/{service_name}/errors",
    description=("All the failed requests for a service"),
    summary="All the failed requests for a service",
)
async def get_service_errors(
    service_name: str,
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent errors for a service."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    services = df["service_name"].unique().tolist()

    if service_name not in services:
        raise HTTPException(status_code=404, detail="Item not found")

    errors = df[
        (df["service_name"] == service_name) & (df["status_code"] >= 500)
    ]
    return Response(content=errors.to_json(orient="records"))


@external_router.get(
    "/service/{service_name}/laggers",
    description=("All the laggers for a service"),
    summary="All the laggers for a service",
)
async def get_service_laggers(
    service_name: str,
    time: int = 30,
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent services in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    services = df["service_name"].unique().tolist()

    if service_name not in services:
        raise HTTPException(status_code=404, detail="Item not found")

    laggers = df[
        (df["service_name"] == service_name) & (df["request_time"] >= time)
    ]
    return Response(content=laggers.to_json(orient="records"))


@external_router.get(
    "/service/{service_name}/stats",
    description=("Statistical breakdown of service requests"),
    summary="Statistical breakdown of service requests",
)
async def get_service_stats(
    service_name: str,
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get all the recent services in memory."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    services = df["service_name"].unique().tolist()

    if service_name not in services:
        raise HTTPException(status_code=404, detail="Item not found")

    service_logs = df[df["service_name"] == service_name]
    return Response(content=service_logs.to_json(orient="records"))


async def status_data() -> List[Dict[str, Any]]:
    """Get the status data as a dict."""
    df = pd.DataFrame([vars(i) for i in total_stats])
    services = df["service_name"].unique().tolist()

    status = []

    for service in services:
        errors = df[
            (df["service_name"] == service) & (df["status_code"] >= 500)
        ]

        service_status = "normal"

        if errors.size > 0:
            service_status = "error"

        status.append(
            {
                "name": service,
                "errors": errors.to_dict(orient="records"),
                "status": service_status,
            }
        )

    return status


@external_router.get(
    "/status",
    description=("Status of all services"),
    summary="Status of all services",
)
async def get_status(
    logger: BoundLogger = Depends(logger_dependency),
) -> Response:
    """Get the current status data."""
    data = await status_data()
    return Response(content=json.dumps(data, indent=4, sort_keys=True))
