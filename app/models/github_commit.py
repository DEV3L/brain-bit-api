class GithubCommit:
    def __init__(self, commit_record: dict, repository_name):
        # TODO: abstract build method
        self.repository = repository_name
        self.commit_date = commit_record['commit']['author']['date']
        self.actor = commit_record['author']['login']
        self.sha = commit_record['sha']
        self.message = commit_record['commit']['message']
        self.html_url = commit_record['html_url']

    def to_json(self):
        return self.__dict__
