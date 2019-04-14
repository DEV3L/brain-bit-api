import json
import os

import requests
from requests import Session

from app.daos.github_commit_dao import GithubCommitDao
from app.daos.github_repository_dao import GithubRepositoryDao
from app.models.github_commit import GithubCommit
from app.models.github_repository import GithubRepository
from app.services.logging_service import LoggingService

logger = LoggingService('github')

DEFAULT_USERNAME = os.environ['GITHUB_USERNAME']
DEFAULT_TOKEN = os.environ['GITHUB_TOKEN']


class GithubHarvester:
    def __init__(self, github_repository_dao: GithubRepositoryDao, github_commit_dao: GithubCommitDao):
        self.github_repository_dao = github_repository_dao
        self.github_commit_dao = github_commit_dao

        self.github_session = build_github_session()

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
