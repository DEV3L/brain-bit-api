from app.daos.tweet_dao import TweetDao
from app.harvesters.twitter.api import get_api
from app.harvesters.twitter.tweets import Tweets


class TwitterHarvester():
    def __init__(self, tweet_dao: TweetDao, screen_name: str):
        self.api = get_api()
        self.tweet_dao = tweet_dao
        self.screen_name = screen_name

    def fetch(self):
        tweets = self.tweet_dao.find_all(query={'actor': self.screen_name})
        tweets_by_id = {tweet['tweet_id']: tweet for tweet in tweets}

        retrieved_tweets = []
        retrieved_tweets.extend(self._fetch('tweet', tweets_by_id))
        retrieved_tweets.extend(self._fetch('favorite', tweets_by_id))

        self._save_tweets(retrieved_tweets, tweets_by_id)

        return retrieved_tweets

    def _fetch(self, tweet_type, tweets_by_id):
        tweets = Tweets(self.api, self.screen_name, tweets_by_id, tweet_type=tweet_type)
        return tweets.get()

    def _save_tweets(self, tweets: list, tweets_by_id: dict):
        _tweets = [tweet for tweet in tweets if tweet['tweet_id'] not in tweets_by_id]

        for tweet in _tweets:
            self.tweet_dao.create(tweet)
