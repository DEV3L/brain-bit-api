import json
import os

import requests
from requests import Session

from app.daos.github_commit_dao import GithubCommitDao
from app.daos.github_event_dao import GithubEventDao
from app.daos.github_repository_dao import GithubRepositoryDao
from app.models.github_commit import GithubCommit
from app.models.github_event import GithubEvent
from app.models.github_repository import GithubRepository
from app.services.logging_service import LoggingService

logger = LoggingService('github_retriever')

DEFAULT_USERNAME = os.environ['GITHUB_USERNAME']
DEFAULT_TOKEN = os.environ['GITHUB_TOKEN']


class GithubHarvester:
    def __init__(self, github_event_dao: GithubEventDao, github_repository_dao: GithubRepositoryDao,
                 github_commit_dao: GithubCommitDao):
        self.github_event_dao = github_event_dao
        self.github_repository_dao = github_repository_dao
        self.github_commit_dao = github_commit_dao

        self.github_session = build_github_session()

    def harvest_events_for_username(self, username, token: str = None):
        github_session = build_github_session(username, token) if token else self.github_session

        github_events = self.github_event_dao.find_all(query={'actor': username})
        github_events_by_id = {github_event['id']: github_event for github_event in github_events}

        page = 0
        records = []

        events = []

        while page == 0 or records:
            if 'message' in records:
                _handle_message(records)
                break

            events.extend(records)

            page = page + 1
            url = f'https://api.github.com/users/{username}/events?page={page}'
            records = json.loads(github_session.get(url).text)

        _events = [event for event in events if event['id'] not in github_events_by_id.keys()]
        for event in _events:
            github_event = GithubEvent(event)
            github_event_record = self.github_event_dao.create(github_event)
            logger.info(
                f'Added github event for {github_event.actor} - {github_event.created_at} - {github_event_record}')

    def harvest_repositories_for_user(self, github_username: str, *, token: str = None):
        github_repositories = self.github_repository_dao.find_all(query={'actor': github_username})
        github_repositories_by_name = {github_repository['name']: github_repository for github_repository in
                                       github_repositories}

        repositories = []

        if token:
            repositories.extend(harvest_session_repositories(github_username, token))
        else:
            repositories.extend(harvest_public_repositories(github_username, self.github_session))

        _repositories = [repository for repository in repositories if
                         repository['full_name'] not in github_repositories_by_name]

        for repository in _repositories:
            github_repository = GithubRepository(repository, github_username)
            self.github_repository_dao.create(github_repository)
            logger.info(f'Added github repository - {github_repository.name}')

        return repositories

    def harvest_commits_for_user_by_repositories(self, username: str, *, token: str = None):
        github_session = build_github_session(username, token) if token else self.github_session
        github_commits = self.github_commit_dao.find_all(query={'actor': username})
        github_commits_by_sha = {commit['sha']: commit for commit in github_commits}

        github_repositories = self.github_repository_dao.find_all(query={'actor': username})

        for repository in github_repositories:
            commits_url = repository['commits_url'][:-6].replace('git/', '')

            if not commits_url:
                continue

            page = 0
            records = []

            commits = []

            while page == 0 or records:
                if 'message' in records:
                    _handle_message(records)
                    break

                _commits = [commit for commit in records if commit['sha'] not in github_commits_by_sha]
                _commits = [commit for commit in _commits if commit['commit']['author']['name'] == username]

                if page > 0 and not records:
                    break

                commits.extend(_commits)

                page = page + 1
                url = f'{commits_url}?page={page}'
                records = json.loads(github_session.get(url).text)

            for commit in commits:
                github_commit = GithubCommit(commit, repository['name'])
                github_commit_id = self.github_commit_dao.create(github_commit)
                logger.info(
                    f'Added github commit - {github_commit.actor} - {github_commit.commit_date} - {github_commit.repository} - {github_commit_id}')

            github_repository_commits = self.github_commit_dao.find_all(
                query={'actor': username, 'repository': repository['name']})

            self.github_repository_dao.update(repository['_id'], {'commits': github_repository_commits})
            logger.info(
                f'Harvester Report: {repository["name"]} - {len(github_repository_commits)} commits for {username}')

    def harvest_commits_for_user_by_missing_push_events(self, username: str):
        github_commits = self.github_commit_dao.find_all(query={'actor': username})
        github_commits_by_sha = {commit['sha']: commit for commit in github_commits}

        # events

        github_events = self.github_event_dao.find_all(query={'actor': username, 'type': 'PushEvent'})

        github_events_by_repository = {}
        for event in github_events:
            repository_events = github_events_by_repository.get(event['repo'], {'commits': []})

            commit_shas = [url.split('/')[-1] for url in event['commits_url']]
            unique_commits = [commit_sha for commit_sha in commit_shas if commit_sha not in github_commits_by_sha]
            repository_events['commits'].extend(unique_commits)
            event_model = {'unique_commits': unique_commits, "commits": repository_events['commits'],
                           "event_created_at": event['created_at']}

            github_events_by_repository[event['repo']] = event_model

        github_events_by_repository = {key: value for key, value in github_events_by_repository.items() if
                                       len(value['unique_commits'])}

        for repository_name, event_model in github_events_by_repository.items():
            for commit in event_model['unique_commits']:
                github_commit = GithubCommit(None, None)
                github_commit.actor = username
                github_commit.commit_date = event_model['event_created_at']
                github_commit.repository = repository_name
                github_commit.sha = commit

                github_commit_id = self.github_commit_dao.create(github_commit)
                logger.info(
                    f'Added github commit - {github_commit.actor} - {github_commit.commit_date} - {github_commit.repository} - {github_commit_id}')

            github_repository_results = self.github_repository_dao.find_all(query={'name': repository_name})
            _github_repository = github_repository_results[0] if len(github_repository_results) else None

            if not _github_repository:
                _github_repository = GithubRepository(None, None)
                _github_repository.actor = username
                _github_repository.name = repository_name
                _github_repository.display_name = repository_name
                _github_repository.created_at = event_model['event_created_at']
                _github_repository.updated_at = event_model['event_created_at']

                self.github_repository_dao.create(_github_repository)
                logger.info(f'Harvester Report: Created repository {repository_name} for {username}')

                github_repository_results = self.github_repository_dao.find_all(query={'name': repository_name})
                _github_repository = github_repository_results[0] if len(github_repository_results) else None

            repository_id = github_repository_results[0]['_id']
            github_repository_commits = self.github_commit_dao.find_all(
                query={'actor': username, 'repository': repository_name})
            self.github_repository_dao.update(repository_id, {'commits': github_repository_commits})
            logger.info(
                f'Harvester Report: {repository_name} - {len(github_repository_commits)} commits for {username}')

        print(github_events_by_repository)


def harvest_session_repositories(username: str, token: str) -> list:
    github_session = build_github_session(username, token)

    page = 0
    records = []

    repositories = []

    while page == 0 or records:
        if 'message' in records:
            _handle_message(records)
            break

        repositories.extend(records)

        page = page + 1
        url = f'https://api.github.com/user/repos?page={page}'
        records = json.loads(github_session.get(url).text)

    return repositories


def harvest_public_repositories(username: str, github_session) -> list:
    page = 0
    records = []

    repositories = []

    while page == 0 or records:
        if 'message' in records:
            _handle_message(records)
            break

        repositories.extend(records)

        page = page + 1
        url = f'https://api.github.com/users/{username}/repos?page={page}'
        records = json.loads(github_session.get(url).text)

    return repositories


def build_github_session(username=DEFAULT_USERNAME, token=DEFAULT_TOKEN) -> Session:
    github_session = requests.Session()
    github_session.auth = (username, token)

    return github_session


def _handle_message(response: dict):
    logger.info(response['message'])

    if response['message'] == 'Bad credentials':
        raise RuntimeError('Bad credentials')
