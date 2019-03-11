import os

from eve import Eve
from flask import render_template, request

from app.authentication.basic_authentication import requires_auth
from app.daos.github_event_dao import GithubEventDao
from app.daos.mongo import MongoDatabase
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

github_event_dao = GithubEventDao(MongoDatabase())


@app.route('/protected-endpoint', methods=['POST'])
@requires_auth
def process():
    parameters = get_json_data(request.get_json(), ('id',))

    return parameters['id']


def _transform_event(github_event: GithubEvent):
    github_event['commits_count'] = len(github_event['commits'])
    return github_event


@app.route('/dashboard', methods=['GET'])
def github_events():
    events_to_display = github_event_dao.find_all(query={'actor': 'DEV3L', 'type': 'PushEvent'})
    events_to_display = [_transform_event(github_event) for github_event in events_to_display]

    commits_count = 0
    repos_to_display_dict = {}

    for github_event in events_to_display:
        repo_name = github_event['repo']
        if repo_name not in repos_to_display_dict:
            repos_to_display_dict[repo_name] = {'name': repo_name, 'commits_count': 0}

        event_commits_count = len(github_event['commits'])

        repo = repos_to_display_dict[repo_name]
        repo['commits_count'] = repo['commits_count'] + event_commits_count
        commits_count += event_commits_count
        repos_to_display_dict[repo_name] = repo

    return render_template('index.html', github_events=events_to_display, github_repos=repos_to_display_dict.values(),
                           commits_count=commits_count)


@app.route("/github_events/<github_event_id>/delete")
def tweet_id_delete(github_event_id):
    github_event_dao.delete_one(github_event_id)
    github_events = github_event_dao.find_all(query={'actor': 'DEV3L', 'type': 'PushEvent'})
    return render_template('index.html', github_events=github_events)


if __name__ == '__main__':
    logger.info("Running Brain-Bit Application!")
    app.run(host=host, port=port, debug=env('DEBUG', default=False))
