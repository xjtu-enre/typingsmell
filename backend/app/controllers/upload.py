from flask import Blueprint, request, current_app
from flask.views import MethodView
from app.utils import Warp, DealFile

proj_upload = Blueprint('proj_upload', __name__, url_prefix='/project')


class Upload(MethodView):
    def post(self):
        files = request.files
        if not bool(files):
            return Warp.fail_warp(301)
        for key in files:
            file_path = key
            py_file = files[file_path]
            if py_file is None:
                current_app.logger.error('文件不存在')
                return Warp.fail_warp(301)

            if not DealFile().allowed_file(py_file.filename):
                current_app.logger.error('文件格式不正确')
                return Warp.fail_warp(207)

            DealFile().save_file(file_path, py_file)
        return Warp.success_warp('项目上传成功')


upload_view = Upload.as_view('proj_upload')

proj_upload.add_url_rule('/uploadold', view_func=upload_view, methods=['POST'])
