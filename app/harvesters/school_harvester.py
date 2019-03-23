import os

from app.models.school_session import SchoolSession
from app.services.logging_service import LoggingService

logger = LoggingService('school')

DEFAULT_USERNAME = os.environ['GITHUB_USERNAME']


class SchoolHarvester:
    def __init__(self, school_session_dao: SchoolSessionDao):
        self.school_session_dao = school_session_dao

    def harvest_sessions_for_username(self, username: str = DEFAULT_USERNAME, token: str = None):
        school_session = SchoolSession()
