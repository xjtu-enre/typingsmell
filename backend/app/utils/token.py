import jwt
import time

from app.basic import Config


class Token:
    @classmethod
    def create_token(cls, user_id: int, user_type: int) -> str:
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'exp': time.time() + 8 * 24 * 60 * 60
        }

        return jwt.encode(payload, Config.get_instance()['SECRET_KEY'], algorithm='HS256')

    @classmethod
    def parse_token(cls, token: str) -> dict:
        token = bytes(token, encoding='utf-8')
        return jwt.decode(token, Config.get_instance()['SECRET_KEY'], 'HS256')
