import sys
import asyncio

# CRITICAL for Windows/Playwright: Force ProactorEventLoopPolicy
# This MUST be the very first thing that happens
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.api_v1.api import api_router
from core.config import settings
from core.database import engine, Base
import logging
import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created on startup
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully.")
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to PriceIntel API"}

if __name__ == "__main__":
    import uvicorn
    # When running directly with python main.py, we force the asyncio loop
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, loop="asyncio")
