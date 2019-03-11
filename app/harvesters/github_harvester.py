import json
import os

import requests
from requests import Session

from app.daos.github_event_dao import GithubEventDao
from app.models.github_event import GithubEvent
from app.services.logging_service import LoggingService

logger = LoggingService('github_retriever')


class GithubHarvester:
    def __init__(self, github_event_dao: GithubEventDao):
        self.github_event_dao = github_event_dao
        self.github_session = build_github_session()

    def harvest_events_for_user(self, github_username):
        github_events = self.github_event_dao.find_all(query={'actor': github_username})
        github_events_by_id = {github_event['id']: github_event for github_event in github_events}

        event_record_ids = []

        page = 1
        events_url = f'https://api.github.com/users/{github_username}/events?page={page}'
        events = json.loads(self.github_session.get(events_url).text)

        while events:
            if 'message' in events:
                logger.info(events['message'])

                if events['message'] == 'Bad credentials':
                    raise RuntimeError('Bad credentials')

                break

            for event in events:
                if event['id'] in github_events_by_id.keys():
                    continue

                github_event = GithubEvent(event)

                github_event_record = self.github_event_dao.create(github_event)
                event_record_ids.append(github_event_record)

            page = page + 1
            events = self._get_events(github_username, page)

        return event_record_ids

    def _get_events(self, github_username, page):
        events_url = f'https://api.github.com/users/{github_username}/events?page={page}'
        return json.loads(self.github_session.get(events_url).text)

    def harvest_repos_for_user(self, github_username):
        github_events = self.github_event_dao.find_all(query={'actor': github_username})
        github_events_by_id = {github_event['id']: github_event for github_event in github_events}

        sessions_page = 1
        sessions_repos = []

        session_user_repos_url = f'https://api.github.com/user/repos?page={sessions_page}'
        session_user_repos = json.loads(self.github_session.get(session_user_repos_url).text)

        while session_user_repos:
            if 'message' in session_user_repos:
                logger.info(events['message'])

                if events['message'] == 'Bad credentials':
                    raise RuntimeError('Bad credentials')

                break

            sessions_repos.extend(session_user_repos)

            sessions_page = sessions_page + 1
            session_user_repos_url = f'https://api.github.com/user/repos?page={sessions_page}'
            session_user_repos = json.loads(self.github_session.get(session_user_repos_url).text)

        username_page = 1
        username_repos = []

        github_username_repos_url = f'https://api.github.com/users/{github_username}/repos'
        github_username_repos = json.loads(self.github_session.get(github_username_repos_url).text)

        while github_username_repos:
            if 'message' in session_user_repos:
                logger.info(events['message'])

                if events['message'] == 'Bad credentials':
                    raise RuntimeError('Bad credentials')

                break

            username_repos.extend(github_username_repos)

            username_page = username_page + 1
            github_username_repos_url = f'https://api.github.com/users/{github_username}/repos?page={username_page}'
            github_username_repos = json.loads(self.github_session.get(github_username_repos_url).text)

        print(sessions_repos)
        print(username_repos)

        return session_user_repos, github_username_repos



DEFAULT_USERNAME = os.environ['GITHUB_USERNAME']
DEFAULT_TOKEN = os.environ['GITHUB_TOKEN']


def build_github_session(username=DEFAULT_USERNAME, token=DEFAULT_TOKEN) -> Session:
    github_session = requests.Session()
    github_session.auth = (username, token)

    return github_session
