import os

from eve import Eve
from flask import render_template, request

from app.authentication.basic_authentication import requires_auth
from app.daos.env import env
from app.daos.tweet_dao import TweetDao
from app.daos.mongo import MongoDatabase
from app.services.logging_service import LoggingService
from app.services.run_service import get_json_data


logger = LoggingService('app').logger
logger.info("Start Brain-Bit API Application!")

port = int(env('PORT'))
host = env('HOST')

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Eve(template_folder=template_dir,
          static_folder=static_dir)

tweet_dao = TweetDao(MongoDatabase())


@app.route('/protected-endpoint', methods=['POST'])
@requires_auth
def process():
    parameters = get_json_data(request.get_json(), ('id',))

    return parameters['id']


@app.route('/dashboard', methods=['GET'])
def parsed_list():
    tweets = tweet_dao.find_all()
    return render_template('index.html', tweets=tweets)


@app.route("/tweets/<tweet_id>/delete")
def tweet_id_delete(tweet_id):
    tweet_dao.delete_one(tweet_id)
    tweets = tweet_dao.find_all()
    return render_template('index.html', tweets=tweets)


if __name__ == '__main__':
    logger.info("Running Brain-Bit Application!")
    app.run(host=host, port=port, debug=env('DEBUG', default=False))
