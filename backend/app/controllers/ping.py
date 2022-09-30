from flask import Blueprint
from flask.views import MethodView
from app.utils import Warp

ping = Blueprint('ping', __name__)


class Ping(MethodView):
    def get(self):
        return Warp.success_warp('get')

    def post(self):
        return Warp.success_warp('post pong')


ping.add_url_rule('/ping', view_func=Ping.as_view('ping'))
