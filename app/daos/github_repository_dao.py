from app.daos.dao import Dao
from app.daos.mongo import MongoDatabase
from app.models.github_repository import GithubRepository


class GithubRepoDao(Dao):
    def __init__(self, mongo_database: MongoDatabase):
        super().__init__(mongo_database, 'github_repos')

    def _to_json(self, object_record: dict) -> GithubRepository:
        github_repo_model = GithubRepository(object_record)
        return github_repo_model
