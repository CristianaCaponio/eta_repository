"""Basic Database Operations"""
import bcrypt
from typing import Dict
from bson import CodecOptions
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import DESCENDING, ReturnDocument


# ------------------------------
# Database Management
# ------------------------------
async def persist_entry(db: AsyncIOMotorDatabase, collection_name: str, entry: Dict):
    '''
    Persist the entry `entry` into collection `collection_name`\n
    :param collection_name: The name of the collection where to persist the entry\n
    :param entry: the entry to be persisted
    '''
    return await __collection_with_option(db, collection_name).insert_one(entry)


async def update_entry(db: AsyncIOMotorDatabase, collection_name: str, where, updated_entry) -> None:
    '''
    Persist the changes performed on `entry`\n
    :param collection_name: The name of the collection the entry belongs to\n
    :param where: the query to be matched by the element that must be updated
    :param updated_entry: the updated entry to be persisted
    '''
    await __collection_with_option(db, collection_name).update_one(where, {'$set': updated_entry})


async def delete_entry(db: AsyncIOMotorDatabase, collection_name: str, query) -> None:
    '''
    Delete rt message
    '''
    return await __collection_with_option(db, collection_name).find_one_and_delete(filter=query, projection=None)


async def update_entry_atomic(db: AsyncIOMotorDatabase,
                              collection_name: str,
                              filter, replacement,
                              sort=[('_id', DESCENDING)],
                              projection=None,
                              return_document=ReturnDocument.AFTER):
    '''
    Update an `entry` in atomic way\n
    :param collection_name: The name of the collection the entry belongs to\n
    :param where: the query to be matched by the element that must be updated
    :param update_query: the query to update the the entry
    :param return_document: choose to return the document before or after the update
    '''
    return await __collection_with_option(db, collection_name).find_one_and_replace(filter,
                                                                                    replacement,
                                                                                    projection,
                                                                                    sort,
                                                                                    return_document=return_document)


def retreive_entry_by_query(db: AsyncIOMotorDatabase,
                            collection_name: str,
                            query,
                            limit,
                            sort=[('_id', DESCENDING)],
                            ) -> AsyncIOMotorCollection:
    '''
    Retreive the entry matching the `query` from collection `collection_name`\n
    :param query: the query used in the retrieval operation
    '''
    return __collection_with_option(db, collection_name).find(query, sort=sort, limit=limit)


def __collection_with_option(db: AsyncIOMotorDatabase, collection_name: str) -> AsyncIOMotorCollection:
    codec_option = CodecOptions(tz_aware=True)
    return db[collection_name].with_options(codec_option)
# ------------------------------


# ------------------------------
# Hashing utilities
# ------------------------------
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Hashing password
    """
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def check_password(password: str, hashed: str) -> bool:
    """
    Checking Password

    Parameters
    ----------
    password : str
    hashed : str

    Returns
    -------
    bool
    """
    return bcrypt.checkpw(password.encode(), hashed.encode())
