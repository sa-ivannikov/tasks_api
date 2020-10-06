import jwt
import os
import datetime


from functools import wraps
from flask import json, Response, request, g
from loguru import logger

from .models import User


class Auth():
    """ Authentification class """

    @staticmethod
    def generate_token(user_id):
        """ Generates jwt for given user """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY'),
                'HS256',
            ).decode('utf-8')
        except Exception:
            return Response(
                mimetype='application/json',
                response=json.dumps({
                    'error': 'error in generating user token'
                }),
                status=400
            )

    @staticmethod
    def decode_token(token):
        """ Decodes jwt """
        re = {
            'data': {},
            'error': {},
        }
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
            re['data'] = {
                'id': payload['sub'],
            }
            return re
        except jwt.ExpiredSignatureError:
            re['error'] = {
                'message': 'token expired. Please, log in'
            }
            return re
        except jwt.InvalidTokenError:
            re['error'] = {
                'message': 'Invalid token.'
            }
            return re

    @staticmethod
    def auth_required(func):
        """ Decorator for protected routes """
        @wraps(func)
        def decorated(*args, **kwargs):
            if 'Authorization' not in request.headers:
                return Response(
                    mimetype="application/json",
                    response=json.dumps(
                        {'error': 'Auth required. Please log in and provide a token in Authorization header'}),
                    status=400,
                )
            token = request.headers.get('Authorization')
            data = Auth.decode_token(token)
            if data['error']:
                return Response(
                    mimetype="application/json",
                    response=json.dumps(data['error']),
                    status=400
                )

            user_id = data['data']['id']
            check_user = User.get_one_user(user_id)
            if not check_user:
                return Response(
                    mimetype="application/json",
                    response=json.dumps(
                        {'error': 'user does not exist, invalid token'}),
                    status=400
                )
            g.user = {'id': user_id}
            return func(*args, **kwargs)
        return decorated
