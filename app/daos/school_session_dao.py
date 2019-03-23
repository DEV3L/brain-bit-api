import pymongo

from app.daos.dao import Dao
from app.daos.mongo import MongoDatabase
from app.models.school_session import SchoolSession


class SchoolSessionDao(Dao):
    def __init__(self, mongo_database: MongoDatabase):
        super().__init__(mongo_database, 'school_sessions')

    def find_all(self, *, query: dict = None) -> list:
        results = [result for result in
                   self._mongo_database.find(self.collection, query).sort("date", pymongo.DESCENDING)]
        return results

    def _to_json(self, object_record: dict) -> SchoolSession:
        school_session = SchoolSession()
        school_session.build_from_record(object_record)

        github_repository = GithubRepository(repository, github_username)
        self.github_repository_dao.create(github_repository)

        return school_session
