import os

from app.daos.github_event_dao import GithubEventDao
from app.daos.github_repository_dao import GithubRepositoryDao
from app.daos.mongo import MongoDatabase
from app.harvesters.github_harvester import GithubHarvester

github_username = os.environ['GITHUB_USERNAME']
github_token = os.environ['GITHUB_TOKEN']

github_harvester = GithubHarvester(GithubEventDao(MongoDatabase()), GithubRepositoryDao(MongoDatabase()))
github_harvester.harvest_events_for_username(github_username, token=github_token)
github_harvester.harvest_repositories_for_user(github_username, token=github_token)
