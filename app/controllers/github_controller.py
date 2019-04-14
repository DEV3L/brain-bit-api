import os
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import render_template, request, jsonify

from app.authentication.basic_authentication import requires_auth
from app.daos.github_commit_dao import GithubCommitDao
from app.daos.github_repository_dao import GithubRepositoryDao
from app.daos.mongo import MongoDatabase
from app.harvesters.github_harvester import GithubHarvester

DATE_FORMAT = "%m/%d/%Y"

# DAOs
github_commit_dao = GithubCommitDao(MongoDatabase())
github_repository_dao = GithubRepositoryDao(MongoDatabase())

# Harvesters
github_harvester = GithubHarvester(github_repository_dao, github_commit_dao)


def register_github_controllers(app):
    @app.route('/authenticate', methods=['POST'])
    @requires_auth
    def authenticate():
        return jsonify({'success': True})

    @app.route('/mine-github', methods=['POST'])
    def mine_github():
        github_username = request.form['github-username']
        github_token = request.form['github-token']

        github_harvester.harvest_repositories_for_user(github_username, token=github_token)
        github_harvester.harvest_commits_for_user_by_repositories(github_username, token=github_token)

        return _github_commits(github_username)

    @app.route('/dashboard', methods=['GET'])
    @app.route('/github-commits', methods=['GET'])
    def github_commits():
        return _github_commits()

    def _github_commits(actor: str = os.environ['GITHUB_USERNAME']):
        current_datetime = datetime.now()
        start_date_default = datetime.strftime(current_datetime - relativedelta(months=3), DATE_FORMAT)
        stop_date_default = datetime.strftime(current_datetime, DATE_FORMAT)

        github_user = request.values.get('actor', actor)
        repository_name = request.values.get('repository-name', '')
        start_date = request.values.get('start-date', start_date_default)
        stop_date = request.values.get('stop-date', stop_date_default)

        start = datetime.strptime(start_date, DATE_FORMAT)
        stop = datetime.strptime(stop_date, DATE_FORMAT)

        days_range = []
        range_date = start
        while range_date < stop:
            range_date = range_date + relativedelta(days=1)
            days_range.append(datetime.strftime(range_date, DATE_FORMAT))

        commits_to_display = github_commit_dao.find_all(query={'actor': github_user})
        commits_to_display = [_transform_commits(github_commit) for github_commit in commits_to_display]

        commits_count_total = len(commits_to_display)

        if repository_name:
            commits_to_display = [commit for commit in commits_to_display if repository_name in commit['repository']]

        commits_to_display = [commit for commit in commits_to_display if commit['message']]
        commits_to_display = [commit for commit in commits_to_display if
                              start <= commit['date']]
        commits_to_display = [commit for commit in commits_to_display if
                              stop >= commit['date']]

        grid_data = []
        for day in days_range:
            day_date = datetime.strptime(day, DATE_FORMAT)

            day_commits = len([commit for commit in commits_to_display if day_date == commit['date']])
            data = {'x': f' new Date({day_date.year}, {day_date.month - 1}, {day_date.day}) ', 'y': day_commits}

            grid_data.append(data)

        return render_template('github_commits.html', github_commits=commits_to_display,
                               commits_count=len(commits_to_display), grid_data=grid_data,
                               commits_count_total=commits_count_total, github_user=github_user,
                               start_date=start_date, stop_date=stop_date, repository_name=repository_name)

    def _transform_commits(github_commit):
        date = github_commit['commit_date'].split('T')[0]
        github_commit['date_display'] = date
        github_commit['date'] = datetime.strptime(date, "%Y-%m-%d")

        message = github_commit['message'].split('\n')[0]
        message = message[:60 if len(message) > 60 else len(message)]
        github_commit['message_display'] = message

        return github_commit

    @app.route('/github-repositories', methods=['GET'])
    def github_repositories():
        github_user = request.values.get('actor', os.environ['GITHUB_USERNAME'])

        repositories_to_display = github_repository_dao.find_all(query={'actor': github_user})
        repositories_to_display = [_transform_repository(github_repository) for github_repository in
                                   repositories_to_display]
        repositories_to_display = [github_repository for github_repository in repositories_to_display if
                                   github_repository['commits_count']]

        commits_count = 0
        for repository in repositories_to_display:
            commits_count += repository['commits_count']

        return render_template('github_repositories.html', github_repositories=repositories_to_display,
                               repositories_count=len(repositories_to_display), commits_count=commits_count,
                               github_user=github_user)

    def _transform_repository(github_repository):
        github_repository['commits_count'] = len(github_repository['commits'])
        return github_repository
