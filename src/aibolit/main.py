#!/usr/bin/env -S uv run --script --no-dev
import asyncio
import uvicorn
from fastapi import FastAPI

# from aibolit.transport.rest.schedules.views import router as schedules_router
from aibolit.transport.rest.users.views import router as users_router

app = FastAPI()
# app.include_router(schedules_router)
app.include_router(users_router)


async def serve_rest():
    config = uvicorn.Config("main:app", host="localhost", port=8000, reload=True)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    from aibolit.transport.grpc.main import serve as serve_grpc

    await asyncio.gather(serve_grpc(), serve_rest())


if __name__ == "__main__":
    asyncio.run(main())
