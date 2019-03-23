import os

from app.daos.csv_dao import load_csv
from app.daos.school_session_dao import SchoolSessionDao
from app.models.school_session import SchoolSession
from app.services.logging_service import LoggingService

logger = LoggingService('school')

DEFAULT_USERNAME = os.environ['GITHUB_USERNAME']


class SchoolHarvester:
    def __init__(self, school_session_dao: SchoolSessionDao):
        self.school_session_dao = school_session_dao

    def harvest_sessions_for_username(self, username: str = DEFAULT_USERNAME, token: str = None):
        school_sessions = self.school_session_dao.find_all(query={'actor': username})
        school_sessions_by_identity = {_build_key(school_session): school_session for school_session in school_sessions}

        path = f'./data/school-{username}.csv'
        school_sessions_data = load_csv(path)

        filtered_school_sessions_data = [record for record in school_sessions_data if
                                         _build_key(record) not in school_sessions_by_identity]
        for school_session_record in filtered_school_sessions_data:
            school_session = SchoolSession()
            school_session.build_from_record(school_session_record, username)
            self.school_session_dao.create(school_session)


def _build_key(record):
    return f'{record["date"]}{record["duration"]}{record["cumulative"]}{record["project"]}'
