import json
import os

import requests
from requests import Session

from app.daos.github_events_dao import GithubEventDao


class GithubRetriever:
    def __init__(self, github_event_dao: GithubEventDao):
        self.github_event_dao = github_event_dao
        self.github_session = GithubRetriever._build_session()

    def collect_events_for_user(self, github_username):
        github_events = self.github_event_dao.find_all(query={'actor': github_username})
        github_events_by_id = {github_event['id']: github_event for github_event in github_events}

        page = 1
        events_url = f'https://api.github.com/users/{github_username}/events?page={page}'
        events = json.loads(self.github_session.get(events_url).text)

        while events:
            if 'message' in events:
                print(events['message'])
                break

            for event in events:
                if event['id'] in github_events_by_id.keys():
                    continue

                github_event = GithubEvent(event)

                github_event_record = github_event_dao.create(github_event)
                print(github_event_record)

            page = page + 1
            events = self._get_events(github_username, page)

    def _get_events(self, github_username, page):
        events_url = f'https://api.github.com/users/{github_username}/events?page={page}'
        return json.loads(self.github_session.get(events_url).text)

    @staticmethod
    def _build_session() -> Session:
        username = os.environ['GITHUB_USERNAME']
        token = os.environ['GITHUB_TOKEN']

        github_session = requests.Session()
        github_session.auth = (username, token)

        return github_session
