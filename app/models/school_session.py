from app.models.model import Model


class SchoolSession(Model):
    def __init__(self):
        if not commit_record:
            self.date = ''
            self.duration = ''
            self.cumulative = ''
            self.project = ''

    def build_from_record(self, school_session_record: dict):
        # self.repository = repository_name
        # self.commit_date = commit_record['commit']['author']['date']
        # self.actor = commit_record['commit']['author']['name']
        # self.sha = commit_record['sha']
        # self.message = commit_record['commit']['message']
        # self.html_url = commit_record['html_url']
        pass
