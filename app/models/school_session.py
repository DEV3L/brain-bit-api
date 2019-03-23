from app.models.model import Model


class SchoolSession(Model):
    def __init__(self):
        self.actor = ''
        self.date = ''
        self.duration = ''
        self.cumulative = ''
        self.project = ''

    def build_from_record(self, school_session_record: dict, actor: str):
        self.__dict__.update(school_session_record)
        self.actor = actor
