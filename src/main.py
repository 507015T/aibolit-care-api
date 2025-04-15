#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI
from schedules.router import router as schedules_router
from users.router import router as users_router

app = FastAPI()
app.include_router(schedules_router)
app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
