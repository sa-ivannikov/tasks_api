from flask import request, Blueprint
from loguru import logger
from marshmallow.exceptions import ValidationError

from tasks.models import User
from tasks.schemas import UserSchema
from tasks.auth import Auth
from tasks.custom_response import custom_response

user_api = Blueprint('users', __name__)
user_schema = UserSchema()


@user_api.route('/register', methods=['POST'])
def create_user():
    """ Creates new user """
    req_data = request.get_json()
    try:
        data = user_schema.load(req_data)
    except ValidationError as validation_error:
        return custom_response(validation_error.messages, 400)

    user_in_db = User.query.filter_by(username=data.get('username')).first()
    if user_in_db:
        message = {
            'error': 'User with this username already exists. Please supply another name'
        }
        return custom_response(message, 400)

    new_user = User(data)
    new_user.save()

    serialized_data = user_schema.dump(new_user)

    token = Auth.generate_token(serialized_data.get('id'))
    return custom_response({
        'jwt': token
    },
        201)


@user_api.route('/login', methods=['POST'])
def login():
    req_data = request.get_json()
    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as validation_error:
        return custom_response(validation_error.messages, 400)

    if not data.get('username'):
        return custom_response({'error': 'no username provided'}, 400)
    if not data.get('password'):
        return custom_response({'error': 'no password provided'}, 400)

    user = User.query.filter_by(username=data.get('username')).first()

    if not user:
        return custom_response({'error': 'invalid credentials'}, 400)

    if not user.check_hash(data.get('password')):
        return custom_response({'error': 'invalid credentials'}, 400)

    serialized_data = user_schema.dump(user)

    token = Auth.generate_token(serialized_data.get('id'))

    return custom_response({'jwt_token': token}, 200)
