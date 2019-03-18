from app.daos.dao import Dao
from app.models.tweet import Tweet


class TweetDao(Dao):
    def __init__(self, mongo_database):
        super().__init__(mongo_database, 'tweets')

    def _to_json(self, object_record: dict) -> Tweet:
        tweet_model = Tweet(object_record['name'])
        return tweet_model

    def find_by_id(self, tweet_id):
        json = self._mongo_database.get(self.collection, tweet_id)
        tweet_model = Tweet('')
        tweet_model.from_json(json)
        return tweet_model
