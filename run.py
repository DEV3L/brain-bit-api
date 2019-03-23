import os
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta
from eve import Eve
from flask import render_template, request, jsonify

from app.authentication.basic_authentication import requires_auth
from app.daos.github_commit_dao import GithubCommitDao
from app.daos.github_event_dao import GithubEventDao
from app.daos.github_repository_dao import GithubRepositoryDao
from app.daos.mongo import MongoDatabase
from app.daos.school_session_dao import SchoolSessionDao
from app.harvesters.github_harvester import GithubHarvester
from app.harvesters.school_harvester import SchoolHarvester
from app.services.logging_service import LoggingService
from app.services.run_service import get_json_data
from app.utils.env import env

logger = LoggingService('app').logger
logger.info("Start Brain-Bit API Application!")

port = int(env('PORT'))
host = env('HOST')

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Eve(template_folder=template_dir,
          static_folder=static_dir)

# DAOs
github_commit_dao = GithubCommitDao(MongoDatabase())
github_event_dao = GithubEventDao(MongoDatabase())
github_repository_dao = GithubRepositoryDao(MongoDatabase())
school_session_dao = SchoolSessionDao(MongoDatabase())

# Harvesters
github_harvester = GithubHarvester(github_event_dao, github_repository_dao, github_commit_dao)
school_harvester = SchoolHarvester(school_session_dao)

DATE_FORMAT = "%m/%d/%Y"


@app.route('/harvest-github', methods=['POST'])
@requires_auth
def harvest_github():
    parameters = get_json_data(request.get_json(), ('github_username',))

    github_username = parameters['github_username']
    github_token = parameters.get('github_token', None)

    github_harvester.harvest_events_for_username(github_username, token=github_token)
    github_harvester.harvest_repositories_for_user(github_username, token=github_token)
    github_harvester.harvest_commits_for_user_by_repositories(github_username, token=github_token)
    github_harvester.harvest_commits_for_user_by_missing_push_events(github_username)

    return jsonify({'success': True})


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


@app.route('/mine-github', methods=['POST'])
def mine_github():
    github_username = request.form['github-username']
    github_token = request.form['github-token']

    github_harvester.harvest_events_for_username(github_username, token=github_token)
    github_harvester.harvest_repositories_for_user(github_username, token=github_token)
    github_harvester.harvest_commits_for_user_by_repositories(github_username, token=github_token)
    github_harvester.harvest_commits_for_user_by_missing_push_events(github_username)

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


@app.route('/github-events', methods=['GET'])
def github_events():
    return _github_events(request)


@app.route("/github_events/<github_event_id>/delete")
def github_event_id_delete(github_event_id):
    github_event_dao.delete_one(github_event_id)

    return _github_events(request)


@app.route('/mine-school', methods=['POST'])
def mine_school():
    actor = request.form['actor']

    school_harvester.harvest_sessions_for_actor(actor)

    return _school_sessions(actor)


@app.route('/school-sessions', methods=['GET'])
def school_sessions():
    return _school_sessions()


def _school_sessions(actor: str = os.environ['GITHUB_USERNAME']):
    current_datetime = datetime.now()
    start_date_default = datetime.strftime(current_datetime - relativedelta(months=3), DATE_FORMAT)
    stop_date_default = datetime.strftime(current_datetime, DATE_FORMAT)

    actor = request.values.get('actor', actor)
    project = request.values.get('project', '')
    start_date = request.values.get('start-date', start_date_default)
    stop_date = request.values.get('stop-date', stop_date_default)

    start = datetime.strptime(start_date, DATE_FORMAT)
    stop = datetime.strptime(stop_date, DATE_FORMAT)

    days_range = []
    range_date = start
    while range_date < stop:
        range_date = range_date + relativedelta(days=1)
        days_range.append(datetime.strftime(range_date, DATE_FORMAT))

    school_sessions_to_display = school_session_dao.find_all(query={'actor': actor})
    school_sessions_to_display = [_transform_school_sessions(school_session) for school_session in
                                  school_sessions_to_display]

    school_sessions_count_total = len(school_sessions_to_display)

    if project:
        school_sessions_to_display = [school_session for school_session in school_sessions_to_display if
                                      project in school_session['project']]

    school_sessions_to_display = [school_session for school_session in school_sessions_to_display if
                                  start <= parser.parse(school_session['date'])]
    school_sessions_to_display = [school_session for school_session in school_sessions_to_display if
                                  stop >= parser.parse(school_session['date'])]

    grid_data = []
    for day in days_range:
        day_date = datetime.strptime(day, DATE_FORMAT)

        # TODO: totals
        day_school_sessions = len(
            [school_session for school_session in school_sessions_to_display if day_date == school_session['date']])
        data = {'x': f' new Date({day_date.year}, {day_date.month - 1}, {day_date.day}) ', 'y': day_school_sessions}

        grid_data.append(data)

    return render_template('school_sessions.html', school_sessions=school_sessions_to_display,
                           school_sessions_count=len(school_sessions_to_display), grid_data=grid_data,
                           school_sessions_count_total=school_sessions_count_total, actor=actor,
                           start_date=start_date, stop_date=stop_date, project=project)


def _transform_school_sessions(school_session):
    return school_session


def _github_events(controller_request):
    github_user = controller_request.values.get('actor', os.environ['GITHUB_USERNAME'])

    events_to_display = github_event_dao.find_all(query={'actor': github_user, 'type': 'PushEvent'})
    events_to_display = [_transform_event(github_event) for github_event in events_to_display]

    repos_to_display_dict, commits_count = _build_repositories(events_to_display)

    return render_template('github_events.html', github_events=events_to_display,
                           github_repos=repos_to_display_dict.values(),
                           commits_count=commits_count, github_user=github_user)


def _transform_event(github_event):
    github_event['commits_count'] = len(github_event['commits'])
    return github_event


def _build_repositories(events):
    repos_to_display_dict = {}
    commits_count = 0

    for github_event in events:
        repo_name = github_event['repo']
        if repo_name not in repos_to_display_dict:
            repos_to_display_dict[repo_name] = {'name': repo_name, 'commits_count': 0}

        event_commits_count = len(github_event['commits'])

        repo = repos_to_display_dict[repo_name]
        repo['commits_count'] = repo['commits_count'] + event_commits_count
        commits_count += event_commits_count
        repos_to_display_dict[repo_name] = repo

    return repos_to_display_dict, commits_count


if __name__ == '__main__':
    logger.info("Running Brain-Bit Application!")
    app.run(host=host, port=port, debug=env('DEBUG', default=False))
