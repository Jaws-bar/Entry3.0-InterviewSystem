from functools import wraps
from binascii import hexlify
from hashlib import pbkdf2_hmac
import ujson
from flask_restful import Resource
from flask import abort, current_app, g, Response
from flask_jwt_extended import get_jwt_identity, get_raw_jwt, jwt_required, jwt_refresh_token_required

from app.models.admin import Admin, AdminTypeEnum


blacklist = set()


def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'deny'
    response.headers['X-Powered-by'] = ''
    response.headers['Server'] = ''

    return response


def auth_required(fn):
    @wraps(fn)
    @jwt_required
    def wrapper(*args, **kwargs):
        account = Admin.query.filter_by(em=get_jwt_identity()).first()

        if account is None:
            abort(403)

        g.user = account.email

        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    @jwt_required
    def wrapper(*args, **kwargs):
        account = Admin.query.filter_by(em=get_jwt_identity()).first()

        if (account is None) or (account.admin_type != AdminTypeEnum.ROOT) :
            abort(403)

        g.user = account.email

        return fn(*args, **kwargs)

    return wrapper


def blacklist_check(fn):
    @wraps(fn)
    @jwt_refresh_token_required
    def wrapper(*args, **kwargs):
        is_blacklisted = get_raw_jwt()['jti'] in blacklist

        if is_blacklisted:
            abort(403)

        return fn(*args, **kwargs)
    return wrapper


class BaseResource(Resource):

    @classmethod
    def unicode_safe_json_dumps(cls, data, status_code=200, **kwargs):
        return Response(
            ujson.dumps(data, ensure_ascii=False),
            status_code,
            content_type='application/json; charset=utf8',
            **kwargs
        )


class Router:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        from app.views.auth import auth
        app.register_blueprint(auth.api.blueprint)

        from . import test
        app.register_blueprint(test.api_1.blueprint)
        app.register_blueprint(test.api_2.blueprint)

        print("[INFO] Router initialized")
