from app.daos.dao import Dao
from app.models.tweet import Tweet


class TweetDao(Dao):
    def __init__(self, mongo_database):
        super().__init__(mongo_database, 'tweets')

    def _to_json(self, object_record: dict) -> GithubEvent:
        tweet_model = Tweet(object_record)
        return tweet_model

    def find_by_id(self, tweet_id):
        json = self._mongo_database.get(self._collection, tweet_id)
        tweet_model = Tweet(None, None, None, None)
        tweet_model.from_json(json)
        return tweet_model
