#!/usr/bin/env -S uv run --script --no-dev
import asyncio
import uvicorn
from fastapi import FastAPI
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / ".." / "grpc_server"))
from schedules.router import router as schedules_router
from users.router import router as users_router

app = FastAPI()
app.include_router(schedules_router)
app.include_router(users_router)


async def serve_rest():
    config = uvicorn.Config("main:app", host="localhost", port=8000, reload=True)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    from grpc_main import serve as serve_grpc

    await asyncio.gather(serve_grpc(), serve_rest())


if __name__ == "__main__":
    asyncio.run(main())
