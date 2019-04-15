import os
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta
from flask import render_template, request

from app.daos.mongo import MongoDatabase
from app.daos.school_session_dao import SchoolSessionDao
from app.harvesters.school_harvester import SchoolHarvester

DATE_FORMAT = "%m/%d/%Y"


# DAOs
school_session_dao = SchoolSessionDao(MongoDatabase())

# Harvesters
school_harvester = SchoolHarvester(school_session_dao)


def register_school_controllers(app):
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

            day_school_sessions = [school_session for school_session in school_sessions_to_display if
                                   day_date == parser.parse(school_session['date'].split(" ")[0])]

            day_duration = 0
            for school_session in day_school_sessions:
                day_duration += float(school_session['duration'])

            data = {'x': f' new Date({day_date.year}, {day_date.month - 1}, {day_date.day}) ', 'y': day_duration}

            grid_data.append(data)

        return render_template('school_sessions.html', school_sessions=school_sessions_to_display,
                               school_sessions_count=len(school_sessions_to_display), grid_data=grid_data,
                               school_sessions_count_total=school_sessions_count_total, actor=actor,
                               start_date=start_date, stop_date=stop_date, project=project)

    def _transform_school_sessions(school_session):
        return school_session
