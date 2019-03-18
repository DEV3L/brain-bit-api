import os

import tweepy


def get_api():
    auth_handler = get_auth_handler()
    return tweepy.API(auth_handler, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def get_auth_handler():
    consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    access_token = os.environ['TWITTER_ACCESS_TOKEN']
    access_token_secret = os.environ['TWITTER_TOKEN_SECRET']

    o_auth_handler = tweepy.OAuthHandler(consumer_key, consumer_secret)
    o_auth_handler.set_access_token(access_token, access_token_secret)

    return o_auth_handler
