import sys
import asyncio

# CRITICAL for Windows/Playwright: Force ProactorEventLoopPolicy
# This MUST be the very first thing that happens
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.api_v1.api import api_router
from core.config import settings
from core.database import engine, Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import os
from contextlib import asynccontextmanager
import traceback
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created on startup
    logging.basicConfig(level=logging.INFO)
    try:
        logging.info(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URL.split('@')[-1]}")
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully.")
    except Exception as e:
        logging.error(f"CRITICAL: Failed to connect to database or create tables: {e}")
        # On Render free tier, we want to see this in logs immediately
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Explicit Origins for Production CORS
origins = [
    "http://localhost:3000",
    "https://scrapper-ai-m9ly.vercel.app",
    "https://scrapper-ai-m9ly-vanshh1703s-projects.vercel.app",
]

# We use allow_credentials=True because we send the token in the Authorization header
# but allow_origins must be explicit.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"GLOBAL EXCEPTION: {exc}")
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": "Check server logs for details"}
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to check DB
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/")
def root():
    return {"message": "Welcome to PriceIntel API"}

if __name__ == "__main__":
    import uvicorn
    # When running directly with python main.py, we force the asyncio loop
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, loop="asyncio")
