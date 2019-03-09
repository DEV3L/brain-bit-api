import os

from bson import ObjectId
from pymongo import MongoClient

from app.daos.env import env


class MongoDatabase:
    def __init__(self):
        db_name = env("MONGODB_NAME")
        mongo_url = env("MONGODB_URI")

        if 'IS_DOCKER' in os.environ:
            client = MongoClient(27017)
        else:
            client = MongoClient(mongo_url)

        self.mongo_db = client[db_name]

    def create(self, collection: str, entity: dict) -> str:
        insert_object = self.mongo_db[collection].insert_one(entity)
        return str(insert_object.inserted_id)

    def get(self, collection: str, id: str):
        return self.mongo_db[collection].find_one({'_id': ObjectId(id)})

    def find(self, collection: str, query: dict = None):
        return self.mongo_db[collection].find(query)
