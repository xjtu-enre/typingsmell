import os.path

from flask import current_app, Blueprint, request, send_file
from flask.views import MethodView
from app.utils import Warp, DealFile
from app.models.errors import ProjectNotFound, FileReadError, DirAnalyzeError
from app.models.manager_files import ManagerFile

ctr_file = Blueprint('ctr_file', __name__)


class CtrFile(MethodView):
    def post(self):
        data = request.json
        project_path = data.get('project_path')
        try:
            dir_list, file_list = DealFile().get_dirs(project_path)
            return Warp.success_warp({'dir_list': dir_list, 'file_list': file_list})
        except ProjectNotFound as e:
            current_app.logger.error(e)
            return Warp.fail_warp(208, '项目不存在')
        except DirAnalyzeError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(208, 'Project Not Found')

    def put(self):
        data = request.json
        project_id = data.get('project_id')
        file_path = data.get('file_path')
        try:
            res = ManagerFile().get_file_text(project_id, file_path)
            return Warp.success_warp(res)
        except FileReadError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(208, 'file get error')
        except ProjectNotFound as e:
            current_app.logger.error(e)
            return Warp.fail_warp(208, 'file not found')


file_view = CtrFile.as_view('ctr_file')
ctr_file.add_url_rule('/file', view_func=file_view, methods=['POST', 'PUT'])
ctr_file.add_url_rule('/file/<int:project_id>', view_func=file_view, methods=['GET'])
ctr_file.add_url_rule('/file', defaults={'project_id': None}, view_func=file_view, methods=['GET'])
