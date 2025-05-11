#!/usr/bin/env -S uv run --script --no-dev
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
import uvicorn
from fastapi import FastAPI

from aibolit.core.logger import get_logger, configure_logging
from aibolit.core.middleware import LoggingMiddleware
from aibolit.transport.rest.schedules.views import router as schedules_router
from aibolit.transport.rest.users.views import router as users_router
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


app = FastAPI(lifespan=lifespan, debug=settings.DEBUG)
app.add_middleware(LoggingMiddleware)
app.include_router(schedules_router)
app.include_router(users_router)


async def serve_rest():
    config = uvicorn.Config("main:app", host=settings.APP_HOST, port=settings.APP_PORT, access_log=False)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    from aibolit.transport.grpc.grpc_client import serve as serve_grpc

    logger.info("Starting GRPC and REST servers...")
    await asyncio.gather(serve_grpc(), serve_rest())


if __name__ == "__main__":
    asyncio.run(main())
