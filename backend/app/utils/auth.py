from functools import wraps
from flask import g, current_app
from app.utils.errors import errors
from app.utils.warp import Warp


class Permission:
    """
    用户角色枚举类
    """
    ADMIN = 0x1
    NORMAL = 0x2

    ROLE_MAP = {
        1: 0x1,
        2: 0x2,
        3: 0x2
    }


def auth_require(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = g.user_type
            current_app.logger.debug(user_role)
            if Permission.ROLE_MAP[int(user_role)] & role != Permission.ROLE_MAP[int(user_role)]:
                return Warp.fail_warp(403, errors['403']), 401
            return func(*args, **kwargs)

        return wrapper

    return decorator
