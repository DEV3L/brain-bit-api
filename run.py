import os

from eve import Eve

from app.controllers.github_controller import register_github_controllers
from app.controllers.school_controller import register_school_controllers
from app.services.logging_service import LoggingService
from app.utils.env import env

logger = LoggingService('app').logger
logger.info("Start Brain-Bit API Application!")

port = int(env('PORT'))
host = env('HOST')

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Eve(template_folder=template_dir,
          static_folder=static_dir)

if __name__ == '__main__':
    logger.info("Running Brain-Bit Application!")
    register_github_controllers(app)
    register_school_controllers(app)
    app.run(host=host, port=port, debug=env('DEBUG', default=False))
