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

# consumer_settings = {
#     "bootstrap.servers": os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092'),
#     "group.id": "RT-Controller-fleetone",
#     # <-------------------------- check this line
#     "heartbeat.interval.ms": os.environ.get('HEARTBEAT_INTERVAL_MS', 6000)
#     # "value.deserializer": "io.confluent.kafka.serializers.KafkaJsonDeserializer"
# }
# consumer_settings_ = ConsumerSettings(**consumer_settings)

# producer_settings = {
#     "bootstrap.servers": os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092'),
#     "message.max.bytes": os.environ.get('MESSAGE_MAX_BYTES', 900485760),
#     "compression.type": os.environ.get('COMPRESSION_TYPE', 'gzip')
# }


# application_conf = {
#     'input.topic': os.environ.get('INPUT_TOPIC_NAME', 'eta_calculation')
# }

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''this code is executed before the application starts taking requests 
    and right after it finishes handling requests, it covers the whole application lifespan'''
    logger.info("the application is ready.")
    yield
    logger.info("the application shut down.")
    logger.info("Done. Bye.")
    
    
# @app.lifespan("startup")
# async def startup_event() -> None:
#     """
#     Register events to initialize/destroy global state (accessible in all
#     the request via request.app.state
#     """

#     logger.info("Secure storage service ready.")

 
#     """
#     Register events to initialize/destroy global state (accessible in all
#     the request via request.app.state
#     """
#     rt_db_settings = RT_DBSettings()
#     #user_db_settings = UserDBSettings()
#     client = motor.motor_asyncio.AsyncIOMotorClient(rt_db_settings.connection_uri,
#                                                     connect=True,
#                                                     tz_aware=True)  # connect now adn detect connection issues
#     # retreive the database specified in the connection URI
#     # user = motor.motor_asyncio.AsyncIOMotorClient(user_db_settings.connection_uri,
#     #                                                 connect=True,
#     #                                                 tz_aware=True)
#     rt_db = client.get_default_database()
#     #user_db = user.get_default_database()

#     app.state.kafka_controller = KafkaController(
#         {"bootstrap.servers": os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092')})
#     app.state.kafka_controller.create_topic(application_conf['input.topic'])

#     logger.info("Starting up. Initializing Database, producer, and consumer")
#     app.state.producer = AIOProducer(producer_settings)
#     app.state.consumer = AIOConsumer(configs=consumer_settings_,
#                                      topics=[
#                                          application_conf['input.topic'],
#                                          'FLEETONE'],
#                                      db=rt_db,
#                                      producer=app.state.producer)

#     app.state.rt_db = rt_db
#     #app.state.user_db = user_db
#     # loop = asyncio.get_event_loop()
#     # loop.create_task(real_time_loop())
#     # loop.run_forever()
#     logger.info("RT service ready.")





# @app.lifespan("shutdown")
# async def shutdown_event() -> None:
#     """
#     Shuting down. Waiting for consumer to stop
#     """
#     logger.info("Shuting down. Waiting for consumer to stop...")
#     app.state.consumer.close()

#     logger.info("Done. Bye")


# async def real_time_loop():
#     while True:
#         try:
#             #await app.state.consumer.poll_loop()
#             await app.state.consumer.poll_loop()
#             logger.info('test')
#             time.sleep(10)
#         except Exception as ex:
#             logger.error(f'main: error in while true loop: {ex}')


if __name__ == "__main__":
    uvicorn.run("main:app",
                host=settings.host,
                port=settings.port,
                log_level=settings.log_level,
                reload=settings.hot_reload)

