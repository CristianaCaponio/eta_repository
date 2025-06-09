"""main application"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from api.eta_calculation_api import eta_api_router
from settings import Settings

import time
import asyncio

settings = Settings()
api_prefix = f'/api/v{settings.api_version_str}'
app = FastAPI(title=settings.project_name,
              version=settings.api_version_str,
              description="Component for eta calculation",
              openapi_url=f"{api_prefix}/openapi.json")

app.include_router(eta_api_router, prefix=api_prefix)

origins = [
    "http://localhost:8010",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    '''this code is executed before the application starts taking requests
    and right after it finishes handling requests, it covers the whole application lifespan'''
    logger.info("the application is ready.")
    yield
    logger.info("the application shut down.")
    logger.info("Done. Bye.")

if __name__ == "__main__":
    uvicorn.run("main:app",
                host=settings.host,
                port=settings.port,
                log_level=settings.log_level,
                reload=settings.hot_reload)