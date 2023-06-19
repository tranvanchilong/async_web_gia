import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
import time
from bson import ObjectId
from .b_functions import b_log
import traceback


class MongoAsyncPipeline:
    def __init__(self, MONGO_URI, MONGODB_DB, MONGODB_COLLECTION):
        self.client = AsyncIOMotorClient(MONGO_URI, retryWrites=False)
        self.db = self.client[MONGODB_DB]
        self.collection = self.db[MONGODB_COLLECTION]
        self.logger = b_log('b_db')
        
    
    async def check_connect(self):
        try:
            await self.client.server_info()
            self.logger.info(f'Db connected')
        except Exception as e:
            self.logger.exception("connect error")

    
    async def insert_item(self, document_, collection_=None):
        if collection_ is None: collection_ = self.collection
        else: collection_ = self.db[collection_]
        try:
            result = await collection_.insert_one(document_)
            self.logger.debug(msg=f'inserted data: {result.inserted_id}')
            return result.inserted_id
        except BulkWriteError as e:
            dup_keys = len([x for x in e.details['writeErrors'] if 'E11000 duplicate key error collection' in x['errmsg']])
            return 'Dupkey'
        except Exception as e:
            if 'E11000 duplicate key error collection' in str(e):
                return 'Dupkey'
            else:
                self.logger.exception("insert error")
                return "error"


    async def do_insert_many(self, documents_, collection_=None):
        if collection_ is None: collection_ = self.collection
        else: collection_ = self.db[collection_]
        try:
            result = await collection_.insert_many(documents_, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as e:
            dup_keys = len([x for x in e.details['writeErrors'] if 'duplicate key error' in x['errmsg']])
            return 'Dupkey', dup_keys
        except Exception as e:
            if 'E11000 duplicate key error collection' in str(e):
                return 'Dupkey', document_
            else:
                return "error", str(traceback.format_exc())
    
    async def create_index(self, collection_, index_, name, unique=False, background=True):
        collection_ = self.db[collection_]
        await collection_.create_index(index_, unique=unique, background=background, name=name)
    

    async def find_one(self, item, collection_=None):
        if collection_ is None: collection_ = self.collection
        else: collection_ = self.db[collection_]
        return await collection_.find_one(item)


    async def update_one(self, _id, update_, collection_=None):
        if collection_ is None: collection_ = self.collection
        else: collection_ = self.db[collection_]
        return await collection_.update_one({'_id': ObjectId(_id)}, {'$set': update_})
