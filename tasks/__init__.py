import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from .models import db, bcrypt
from .user_blueprint import user_api
from .task_blueprint import tasks_api
from .auth import Auth

def create_app(test_config=None):
    """ App factory """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI'),
    )

    if test_config is None:
        # Load instance config, if any, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test config
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    bcrypt.init_app(app)
    db.init_app(app)

    app.register_blueprint(user_api, url_prefix='/api/users')
    app.register_blueprint(tasks_api, url_prefix='/api/tasks')

    
    @app.route('/')
    @Auth.auth_required
    def test():
        return 'IT WORKS'

    return app