"""main application"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from controller.db.db_setting import ROUTE_DBSettings
import multiprocessing
from socket_service import SocketService
from api.eta_calculation_api import eta_api_router
from settings import Settings
import motor.motor_asyncio

import time
import asyncio

settings = Settings()
api_prefix = f'/follow_track_api'
app = FastAPI(title=settings.project_name,
              version=settings.api_version_str,
              description="Component for eta calculation",
              openapi_url=f"{api_prefix}/openapi.json")

app.include_router(eta_api_router, prefix=api_prefix)

origins = [
    "http://localhost:****",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def socket_thread():
    ngs_socket = SocketService()
    ngs_socket.run_forever()


@app.on_event("startup")
async def startup_event() -> None:
    """
    Register events to initialize/destroy global state (accessible in all
    the request via request.app.state
    """

    logger.info("Follow Track service ready.")

    """
    Register events to initialize/destroy global state (accessible in all
    the request via request.app.state
    """
    route_db_settings = ROUTE_DBSettings()
    client = motor.motor_asyncio.AsyncIOMotorClient(route_db_settings.connection_uri,
                                                    connect=True,
                                                    tz_aware=True)  # connect now adn detect connection issues

    route_db = client.get_default_database()

    # --------------- SOCKET -----------------------------------------------------------

    app.state.all_processes = []
    process = multiprocessing.Process(target=socket_thread, args=())
    process.start()
    app.state.all_processes.append(process)

    app.state.route_db = route_db
    logger.info("Follow Track service ready.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Shuting down. Waiting for consumer to stop
    """
    logger.info("Shuting down. Waiting for consumer to stop...")
    app.state.consumer.close()
    logger.info("close socket processes....")
    for process in app.state.all_processes:
        process.terminate()

    logger.info("Done. Bye")


if __name__ == "__main__":
    uvicorn.run("main:app",
                host=settings.host,
                port=settings.port,
                log_level=settings.log_level,
                reload=settings.hot_reload)
