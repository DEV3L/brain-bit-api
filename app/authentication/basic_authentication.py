from functools import wraps

from flask import request, Response

from app.daos.env import env


def check_auth(username, password):
    is_valid_username = username == env('AUTH_USERNAME')
    is_valid_password = password == env('AUTH_PASSWORD')

    return is_valid_username and is_valid_password


def authenticate():
    return Response('Invalid authentication', 418, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(outer_function):
    @wraps(outer_function)
    def decorated(*args, **kwargs):
        authorization = request.authorization
        if not authorization or not check_auth(authorization.username, authorization.password):
            return authenticate()
        return outer_function(*args, **kwargs)

    return decorated
