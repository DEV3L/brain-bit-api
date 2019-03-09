from bson import ObjectId

from app.models.tweet import Tweet


class TweetDao:
    def __init__(self, mongo_database):
        self._mongo_database = mongo_database
        self._collection = 'tweets'

    def create(self, tweet_model: Tweet):
        json = tweet_model.to_json()
        tweet_id = self._mongo_database.create(self._collection, json)
        return tweet_id

    def find_all(self):
        results = [result for result in self._mongo_database.find(self._collection, None)]
        return results

    def find_by_id(self, tweet_id):
        json = self._mongo_database.get(self._collection, tweet_id)
        tweet_model = Tweet(None, None, None, None)
        tweet_model.from_json(json)
        return tweet_model

    def update(self, tweet_id, tweet_model):
        json = tweet_model.to_json()
        return self._mongo_database.mongo_db[self._collection].update_one(
            {'_id': ObjectId(tweet_id)}, {"$set": json})

    def delete_one(self, _id: str):
        return self._mongo_database.mongo_db[self._collection].delete_one({'_id': ObjectId(_id)})
