import json
import os

import requests

from app.daos.github_events_dao import GithubEventDao
from app.daos.mongo import MongoDatabase
from app.models.github_event import GithubEvent

github_event_dao = GithubEventDao(MongoDatabase())

username = os.environ['GITHUB_USERNAME']
token = os.environ['GITHUB_TOKEN']

github_events = github_event_dao.find_all(query={'actor': username})
github_events_by_id = {github_event['id']: github_event for github_event in github_events}

page = int(len(github_events) / 30) + 1

if page == 10:
    print("Github 300 event history limit, starting at first page for new records")
    page = 1

events_url = f'https://api.github.com/users/{username}/events?page={page}&type=PushEvent'

# create a re-usable session object with the user creds in-built
github_session = requests.Session()
github_session.auth = (username, token)

events = json.loads(github_session.get(events_url).text)

while events:
    if 'message' in events:
        print(events['message'])
        break

    for event in events:
        if event['id'] in github_events_by_id.keys():
            continue

        github_event = GithubEvent(event)

        github_event_record = github_event_dao.create(github_event)
        print(github_event_record)

    page = page + 1
    events_url = f'https://api.github.com/users/{username}/events?page={page}'
    events = json.loads(github_session.get(events_url).text)

print()
