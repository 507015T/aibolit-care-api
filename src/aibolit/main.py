#!/usr/bin/env -S uv run --script --no-dev
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
import uvicorn
from fastapi import FastAPI

from aibolit.core.logger import get_logger, configure_logging
from aibolit.core.middleware import LoggingMiddleware
from aibolit.transport.views.schedules import router as schedules_router
from aibolit.transport.views.users import router as users_router
from aibolit.core.database import engine
from aibolit.core.config import settings

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[dict[str, Any], None]:
    db_engine = engine
    yield {
        "db_engine": engine,
    }
    logger.info(f"OUR FRIENDLY {app} SHUTDOWN")
    await db_engine.dispose()


def make_app() -> FastAPI:
    description = (
        "AibolitCare is a scheduling system for medical services."
        "It provides APIs to manage appointment schedules and time slots for taking medications."
    )
    app = FastAPI(lifespan=lifespan, debug=settings.DEBUG, title="AibolitCare API", description=description)
    app.add_middleware(LoggingMiddleware)
    app.include_router(schedules_router)
    app.include_router(users_router)
    return app


app = make_app()


async def serve_rest():
    config = uvicorn.Config(app=app, host=settings.APP_HOST, port=settings.APP_PORT, access_log=False)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    from aibolit.grpc.grpc_client import serve as serve_grpc

    logger.info("Starting GRPC and REST servers...")
    await asyncio.gather(serve_grpc(), serve_rest())


if __name__ == "__main__":
    import sys
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
