class GithubEvent:
    def __init__(self, event_record: dict):
        self.id = event_record['id']
        self.type = event_record['type']
        self.created_at = event_record['created_at']
        self.actor = event_record['actor']['login']
        self.repo = event_record['repo']['name']
        self.repo_url = event_record['repo']['url']
        self.commits = [commit['message'] for commit in event_record['payload']['commits']] if 'commits' in \
                                                                                               event_record[
                                                                                                   'payload'] else []
        self.commits_url = [commit['url'] for commit in event_record['payload']['commits']] if 'commits' in \
                                                                                               event_record[
                                                                                                   'payload'] else []

    def to_json(self):
        return self.__dict__
