from flask import jsonify
from app.utils.errors import errors


class Warp:
    @classmethod
    def success_warp(cls, data):
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': data
        })

    @classmethod
    def fail_warp(cls, code, msg=None):
        if msg is None:
            temp = errors.get(str(code))
        else:
            temp = msg

        return jsonify({
            'code': code,
            'msg': temp,
            'data': None
        })
