from app.daos.github_event_dao import GithubEventDao
from app.daos.mongo import MongoDatabase
from app.harvesters.github_harvester import GithubHarvester

github_username = 'DEV3L'

github_retriever = GithubHarvester(GithubEventDao(MongoDatabase()))
github_retriever.harvest_events_for_user(github_username)
