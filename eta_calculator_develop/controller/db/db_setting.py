"""Database Settings"""
import os
import motor.motor_asyncio
from loguru import logger
from fastapi.params import Depends
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase


class ROUTE_DBSettings():
    """
    Settings class for database connection
    """

    domain = os.environ.get('DB_DOMAIN', '_______')
    mongo_base_url = f"database.{domain}"
    mongo_port = str(os.environ.get('DB_MONGO_PORT', 00000))
    mongo_nodes = int(os.environ.get('DB_MONGO_NODES', 0))
    hosts = []
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    database = os.environ.get('DB_DATABASE')
    auth_source = os.environ.get('DB_AUTH_SOURCE', '______')
    replica_set = os.environ.get('DB_REPLICA_SET', '______')
    read_preference = 'primary'
    connection_uri = ""
    integration_test = os.environ.get('INTEGRATION_TEST', False)

    def __init__(self) -> None:
        self.hosts = [f'mongo-{i:02}.{self.mongo_base_url}:{
            self.mongo_port}' for i in range(1, self.mongo_nodes+1)]
        if self.integration_test:
            self.connection_uri = f'mongodb://{self.username}:{self.password}@{self.domain}:{self.mongo_port}/{
                self.database}?authSource={self.auth_source}&readPreference={self.read_preference}'
        else:
            self.connection_uri = f"mongodb://{self.username}:{self.password}@{','.join(self.hosts)}/{self.database}?authSource={
                self.auth_source}&replicaSet={self.replica_set}&readPreference={self.read_preference}&ssl=true"


async def get_db(request: Request):
    """
    Get database object from state app
    """

    route_db: AsyncIOMotorDatabase = request.app.state.route_db
    return route_db


ROUTE_DBDependency = Depends(get_db)
