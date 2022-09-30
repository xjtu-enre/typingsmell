import warnings

from flask import current_app, Blueprint, request
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from app.models.errors import ProjectNotFound, ProjectHasExist
from app.utils import Warp
from app.models.manager_project import ManagerProject

ctr_project = Blueprint('ctr_project', __name__)


class CtrProject(MethodView):
    def get(self):
        args = request.args
        try:
            current_app.logger.debug(args.get('limit'))
            limit = int(args.get('limit'))
        except (TypeError, ValueError):
            limit = 10
        try:
            current_app.logger.debug(args.get('page'))
            page = int(args.get('page'))
        except (TypeError, ValueError):
            page = 0
        key = args.get('key')
        try:
            res = ManagerProject(page=page, limit=limit, kwds=key if key is not None else '').get_all_project()
            return Warp.success_warp(res.__dict__)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectNotFound as e:
            current_app.logger.error(e)
            return Warp.fail_warp(403, '项目不存在')

    def post(self):
        warnings.warn("warning!This API is deprecated!", DeprecationWarning)
        data = request.json
        project_name = data.get('project_name')
        version = data.get('version')
        file_count = data.get('file')
        code_url = data.get('code_url')
        star = data.get('star')
        if project_name is None or project_name == '' or file_count is None or version is None:
            current_app.logger.error('项目名不能为空', str({'name': project_name}))
            return Warp.fail_warp(301, '项目名不能为空')
        try:
            ManagerProject().add_project(project_name, version, file_count, code_url, star)
            return Warp.success_warp('项目上传成功')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectHasExist as e:
            current_app.logger.error(e)
            return Warp.fail_warp(206)

    def delete(self, project_id):
        try:
            ManagerProject(project_id=project_id).delete_project()
            return Warp.success_warp('删除成功')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectNotFound as e:
            current_app.logger.error(e)
            return Warp.fail_warp(208, '项目不存在')


project_view = CtrProject.as_view('ctr_project')
ctr_project.add_url_rule('/project', view_func=project_view, methods=['GET'])
ctr_project.add_url_rule('/project', view_func=project_view, methods=['POST'])
ctr_project.add_url_rule('/project/<int:project_id>', view_func=project_view, methods=['DELETE'])
