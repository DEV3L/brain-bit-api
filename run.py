import os

from eve import Eve
from flask import render_template, request, jsonify

from app.authentication.basic_authentication import requires_auth
from app.daos.github_event_dao import GithubEventDao
from app.daos.github_repository_dao import GithubRepositoryDao
from app.daos.mongo import MongoDatabase
from app.harvesters.github_harvester import GithubHarvester
from app.models.github_event import GithubEvent
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
github_event_dao = GithubEventDao(MongoDatabase())
github_repository_dao = GithubRepositoryDao(MongoDatabase())

# Harvesters
github_harvester = GithubHarvester(github_event_dao, github_repository_dao)


@app.route('/harvest-github', methods=['POST'])
@requires_auth
def harvest_github_events():
    parameters = get_json_data(request.get_json(), ('github_username',))

    github_username = parameters['github_username']
    github_token = parameters.get('github_token', None)

    github_harvester.harvest_events_for_username(github_username, token=github_token)
    github_harvester.harvest_repositories_for_user(github_username, token=github_token)

    return jsonify({'success': True})


@app.route('/github-repositories', methods=['GET'])
def github_repositories():
    github_user = request.values.get('actor', os.environ['GITHUB_USERNAME'])

    repositories_to_display = github_repository_dao.find_all(query={'actor': github_user})

    return render_template('github_repositories.html', github_repositories=repositories_to_display,
                           repositories_count=len(repositories_to_display), github_user=github_user)


@app.route('/dashboard', methods=['GET'])
def github_events():
    return _github_dashboard(request)


@app.route("/github_events/<github_event_id>/delete")
def github_event_id_delete(github_event_id):
    github_event_dao.delete_one(github_event_id)

    return _github_dashboard(request)


def _github_dashboard(controller_request):
    github_user = controller_request.values.get('actor', os.environ['GITHUB_USERNAME'])

    events_to_display = github_event_dao.find_all(query={'actor': github_user, 'type': 'PushEvent'})
    events_to_display = [_transform_event(github_event) for github_event in events_to_display]

    repos_to_display_dict, commits_count = _build_repositories(events_to_display)

    return render_template('index.html', github_events=events_to_display, github_repos=repos_to_display_dict.values(),
                           commits_count=commits_count, github_user=github_user)


def _transform_event(github_event: GithubEvent):
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
