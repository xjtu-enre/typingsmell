from flask import Blueprint, current_app, request
from flask.views import MethodView
from app.utils import Warp
from algorithm.pratice import Recommend, Tool
from app.models.errors import ProjectNotFound
from app.models.manager_recommend import ManagerRec

ctr_recommend = Blueprint('recommend', __name__)


class CtrRecommend(MethodView):
    def post(self):
        data = request.json
        try:
            project_id = data.get('project_id')
            feature = data.get('feature')
            top = data.get('top')
            res = ManagerRec().get_recommend(project_id, feature, top)
            return Warp.success_warp({'recommend': res})
        except ProjectNotFound as e:
            current_app.logger.error(e)
            return Warp.fail_warp('recommend error')


recommend_view = CtrRecommend.as_view('proj_recommend')
ctr_recommend.add_url_rule('/recommend', view_func=recommend_view, methods=['POST'])
