from flask import Blueprint, current_app
from flask.views import MethodView
from pathlib import Path
from app.utils import Warp
from algorithm.pratice import Pattern
from sqlalchemy.exc import SQLAlchemyError
from app.models.errors import ProjectNotFound, UsageNotExist, GitFetchError, ConcurrencyError
from app.models.manager_usage import ManagerUsage

ctr_usage = Blueprint('usage', __name__)


class CtrUsage(MethodView):

    def get(self, project_id):
        if project_id is None:
            try:
                res = ManagerUsage().get_all_usage()

                return Warp.success_warp(res.__dict__)
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目不存在')
            except UsageNotExist as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目类型使用不存在')
        else:
            try:
                res = ManagerUsage().get_project_usage(project_id)
                return Warp.success_warp(res)
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目不存在')
            except UsageNotExist as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目类型使用率不存在')
            except GitFetchError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, 'Project Git Fetch Failed')
            except ConcurrencyError as e:
                return Warp.fail_warp(503, str(e.args[0]))
            except Exception as e:
                print(e)
                return Warp.fail_warp(500, '未知错误')


usage_view = CtrUsage.as_view('proj_usage')
ctr_usage.add_url_rule('/usage', defaults={'project_id': None}, view_func=usage_view, methods=['GET'])
ctr_usage.add_url_rule('/usage/<int:project_id>', view_func=usage_view, methods=['GET'])
