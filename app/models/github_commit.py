class GithubCommit:
    def __init__(self, commit_record: dict, repository_name):
        if not commit_record:
            self.repository = ''
            self.commit_date = ''
            self.actor = ''
            self.sha = ''
            self.message = ''
            self.html_url = ''

            return

        # TODO: abstract build method
        self.repository = repository_name
        self.commit_date = commit_record['commit']['author']['date']
        self.actor = commit_record['commit']['author']['name']
        self.sha = commit_record['sha']
        self.message = commit_record['commit']['message']
        self.html_url = commit_record['html_url']

    def to_json(self):
        return self.__dict__
