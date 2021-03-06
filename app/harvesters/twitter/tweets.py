from tweepy import API
from tweepy import Cursor


class Tweets:
    def __init__(self, twitter_api: API, screen_name: str, tweets_by_id: dict, *, tweet_type: str = 'favorite'):
        self.tweet_type = tweet_type
        self.screen_name = screen_name
        self.tweets_by_id = tweets_by_id

        self._twitter_api = twitter_api
        self._twitter_api_type = twitter_api.favorites if 'favorite' == tweet_type else twitter_api.user_timeline

    def get(self):
        tweets = self._get_from_twitter()
        return tweets

    def _get_from_twitter(self):
        retrieved_tweets = []
        for call_response in self._call():
            tweet_model = self._get_tweet(call_response)
            retrieved_tweets.append(tweet_model)

        return retrieved_tweets

    def _call(self):
        yield from Cursor(self._twitter_api_type, self.screen_name, tweet_mode='extended', count=50).items()

    def _get_tweet(self, call_response):
        full_text = self.extract_full_text(call_response)
        urls = self.extract_urls(call_response)
        #
        # tweet_model = Tweet(
        #     screen_name=self.screen_name,
        #     id=call_response.id,
        #     created_at=call_response.created_at,
        #     full_text=full_text,
        #     hashtags=self.extract_hashtags(call_response),
        #     urls='|'.join(urls),
        #     type=self.tweet_type,
        # )
        #
        # pickled_response = serialize(call_response)
        # raw_data = TweetRawData(tweet=tweet_model, raw_data=pickled_response)
        #
        # tweet_model.tweet_raw_data.append(raw_data)
        # return tweet_model
        return {'full_text': full_text, 'urls': urls}

    @staticmethod
    def extract_full_text(call_response):
        full_text = call_response.full_text
        if hasattr(call_response, 'retweeted_status'):
            full_text = call_response.retweeted_status.full_text
        return full_text

    @staticmethod
    def extract_hashtags(call_response):
        return '|'.join([hashtag['text'] for hashtag in call_response.entities['hashtags']])

    @staticmethod
    def extract_urls(call_response):
        urls = [url['expanded_url'] for url in call_response.entities['urls']]
        urls = Tweets._remove_ignore_urls(urls)

        if hasattr(call_response, 'retweeted_status'):
            if not urls:
                urls = [url['expanded_url'] for url in call_response.retweeted_status.entities['urls']]
                urls = Tweets._remove_ignore_urls(urls)

        return urls

    @staticmethod
    def _remove_ignore_urls(urls: list):
        ignore_twitter_urls = ['https://twitter.com/', 'https://github.com/']
        _urls = []

        for url in urls:
            found = False
            for ignore_url in ignore_twitter_urls:
                if ignore_url in url:
                    found = True
                    break

            if not found:
                _urls.append(url)
        return _urls
