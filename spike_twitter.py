from app.daos.mongo import MongoDatabase
from app.daos.tweet_dao import TweetDao
from app.harvesters.twitter_harvester import TwitterHarvester

twitter_harvester = TwitterHarvester(TweetDao(MongoDatabase()), 'dev3l_')
twitter_harvester.fetch()
