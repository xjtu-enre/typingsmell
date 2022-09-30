import warnings

from flask import Blueprint, current_app
from flask.views import MethodView
from pathlib import Path
from app.utils import Warp
from algorithm import CovEntry
from sqlalchemy.exc import SQLAlchemyError
from app.models.errors import ProjectNotFound, PatternNotExist, GitFetchError, ConcurrencyError
from app.models.manager_pattern import ManagerPattern

ctr_pattern = Blueprint('pattern', __name__)


class CtrPattern(MethodView):
    def post(self):
        warnings.warn("CtrPattern.post API is deprecated", DeprecationWarning)
        src_dir = Path("D:/graduate/THProfiler-main/TypingPatternDetection")
        project_name = src_dir.name
        CovEntry(src_dir, src_dir, project_name)
        return Warp.success_warp('类型使用情况检查成功')

    def get(self, project_id):
        if project_id is None:
            try:
                res = ManagerPattern().get_all_pattern()
                return Warp.success_warp(res.__dict__)
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目不存在')
            except PatternNotExist as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目类型使用不存在')
            except GitFetchError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, 'Project Git Fetch Failed')
        else:
            try:
                pattern_count, pattern_info = ManagerPattern().get_project_pattern(project_id)
                return Warp.success_warp({"pattern_count": pattern_count, "pattern_info": pattern_info})
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目不存在')
            except PatternNotExist as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目复杂类型实践不存在')
            except ConcurrencyError as e:
                return Warp.fail_warp(503, str(e.args[0]))
            except Exception as e:
                print(e)
                return Warp.fail_warp(500, '未知错误')


pattern_view = CtrPattern.as_view('proj_pattern')
ctr_pattern.add_url_rule('/pattern', view_func=pattern_view, methods=['POST'])
# ctr_pattern.add_url_rule('/pattern', defaults={'project_id': None}, view_func=pattern_view, methods=['GET'])
ctr_pattern.add_url_rule('/pattern/<int:project_id>', view_func=pattern_view, methods=['GET'])
