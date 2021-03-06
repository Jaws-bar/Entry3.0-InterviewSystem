from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from app.views import Router, after_request
from app.models import SQLAlchemy


def create_app(*config_cls):
    """
    Creates Flask instance & initialize
    Returns:
        Flask
    """
    print('[INFO] Flask application initialized with {}'.format([config.__name__ for config in config_cls]))

    app_ = Flask(__name__)

    for config in config_cls:
        app_.config.from_object(config)

    JWTManager().init_app(app_)
    SQLAlchemy().init_app(app_)
    Router().init_app(app_)
    Swagger(template=app_.config['SWAGGER_TEMPLATE']).init_app(app_)

    app_.after_request(after_request)

    return app_