class GithubRepository:
    def __init__(self, repo_record: dict, actor: str):
        if not repo_record:
            self.actor = ''
            self.id = ''
            self.name = ''
            self.display_name = ''
            self.private = ''
            self.owner = ''
            self.repo_url = ''
            self.commits_url = ''
            self.labels_url = ''
            self.created_at = ''
            self.updated_at = ''
            self.commits = ''
            return

        self.actor = actor
        self.id = repo_record['id']
        self.name = repo_record['full_name']
        self.display_name = repo_record['name']
        self.private = repo_record['private']
        self.owner = repo_record['owner']['login']
        self.repo_url = repo_record['html_url']
        self.commits_url = repo_record['git_commits_url']
        self.labels_url = repo_record['labels_url']
        self.created_at = repo_record['created_at']
        self.updated_at = repo_record['updated_at']
        self.commits = repo_record.get('commits', [])

    def to_json(self):
        return self.__dict__
