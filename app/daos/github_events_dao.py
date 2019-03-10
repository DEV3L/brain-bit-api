from app.daos.dao import Dao
from app.models.github_event import GithubEvent


class GithubEventDao(Dao):
    def __init__(self, mongo_database):
        super().__init__(mongo_database, 'github_events')

    def _to_json(self, object_record: dict) -> GithubEvent:
        github_event_model = GithubEvent(object_record)
        return github_event_model
