import json
import os
from loguru import logger
from typing import List
from .basic_ops import update_entry_atomic, persist_entry, retreive_entry_by_query, delete_entry
from motor.motor_asyncio import AsyncIOMotorDatabase
from model.travel_data import TravelData
from datetime import datetime


COLLECTION_NAME = os.environ.get('DB_COLLECTION', 'route_object')


class FollowTrackDB(object):

    @staticmethod
    async def add_new_object(db: AsyncIOMotorDatabase, route_objet) -> bool:
        """
        insert new route object in database
        """
        try:
            dict_route_objet = route_objet.mongo()
            result = await persist_entry(db, COLLECTION_NAME, dict_route_objet)
            if result is not None:
                return True
            return False
        except Exception as ex:
            logger.error(f'follow_track_db.add_new_object, error:{ex}')
            return False

    @staticmethod
    async def get_route_object(db: AsyncIOMotorDatabase, ginc: str) -> List[TravelData]:
        """
        get Travel Data object based on GINC
        """
        try:
            result = [TravelData.parse_mongo(match) async for match in retreive_entry_by_query(db,
                                                                                               COLLECTION_NAME,
                                                                                               {'ginc': ginc},
                                                                                               1
                                                                                               )]

            # logger.info(result)
            return result
        except Exception as ex:
            logger.error(f'follow_track_db.get_route_object, error:{ex}')
            return None

    @staticmethod
    async def get_route_object_by_date(db: AsyncIOMotorDatabase, date: str) -> List[TravelData]:
        """
        get Travel Data object based on GINC
        """
        try:
            result = [TravelData.parse_mongo(match) async for match in retreive_entry_by_query(db,
                                                                                               COLLECTION_NAME,
                                                                                               {'personal_id': date},
                                                                                               1
                                                                                               )]

            # logger.info(result)
            return result
        except Exception as ex:
            logger.error(f'follow_track_db.get_route_object, error:{ex}')
            return None

    @staticmethod
    async def delete_route_object(db: AsyncIOMotorDatabase, ginc: str) -> bool:
        '''
        delete 
        '''
        try:
            result = await delete_entry(db, COLLECTION_NAME, {'ginc': ginc})
            if result is not None:
                return True
            return False
        except Exception as ex:
            logger.error(f'follow_track_db.delete_route_object, error:{ex}')
            return False

    @staticmethod
    async def update_route_object(db: AsyncIOMotorDatabase, new_route_object: TravelData) -> bool:
        """
        update the route object
        """
        try:
            new_route_object_dict = new_route_object.mongo()
            result = await update_entry_atomic(db, COLLECTION_NAME, {'ginc': new_route_object.ginc}, new_route_object_dict)
            if result is not None:
                return True
            return False
        except Exception as ex:
            logger.error(f'follow_track_db.update_route_object, error:{ex}')
            return False
