class GithubRepository:
    def __init__(self, repo_record: dict):
        self.id = repo_record['id']
        self.name = repo_record['full_name']
        self.display_name = repo_record['name']
        self.private = repo_record['private']
        self.owner = repo_record['owner']['login']

        self.repo_url = repo_record['html_url']
        self.commits_url = repo_record['git_commits_url']
        self.labels_url = repo_record['labels_url']

    def to_json(self):
        return self.__dict__
