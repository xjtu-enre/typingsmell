from flask import Blueprint, request, g, current_app
from jwt.exceptions import ExpiredSignatureError, DecodeError
from app.utils import errors, Warp, Token


def jwt_middleware(app: Blueprint):
    @app.before_request
    def decode_token():
        if request.method != 'OPTIONS':
            token = request.headers.get('Authorization')
            if token is None:
                current_app.logger.warn(errors['402'])
                return Warp.fail_warp(402), 401

            try:
                jwt = Token.parse_token(token)
                user_id, user_type = jwt['user_id'], jwt['user_type']
                g.user_id, g.user_type = user_id, user_type

                current_app.logger.info('当前登录用户 id 为 %d, 用户类型为 %d', user_id, user_type)
            except ExpiredSignatureError:
                current_app.logger.warn(errors['404'])
                return Warp.fail_warp(404), 401
            except DecodeError:
                current_app.logger.warn(errors['405'])
                return Warp.fail_warp(405), 401
