import pymongo

from app.daos.dao import Dao
from app.daos.mongo import MongoDatabase
from app.models.github_repository import GithubRepository


class GithubCommitDao(Dao):
    def __init__(self, mongo_database: MongoDatabase):
        super().__init__(mongo_database, 'github_commits')

    def find_all(self, *, query: dict = None) -> list:
        results = [result for result in
                   self._mongo_database.find(self.collection, query).sort("commit_date", pymongo.DESCENDING)]
        return results

    def _to_json(self, object_record: dict) -> GithubRepository:
        github_repo_model = GithubRepository(object_record)
        return github_repo_model
