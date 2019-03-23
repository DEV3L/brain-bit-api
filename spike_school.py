import os

from app.daos.mongo import MongoDatabase
from app.daos.school_session_dao import SchoolSessionDao
from app.harvesters.school_harvester import SchoolHarvester

github_username = os.environ['GITHUB_USERNAME']

github_harvester = SchoolHarvester(SchoolSessionDao(MongoDatabase()))
github_harvester.harvest_sessions_for_username(github_username)
