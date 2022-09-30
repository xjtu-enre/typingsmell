from flask import Blueprint, current_app, request
from flask.views import MethodView
from pathlib import Path

from app.models.manager_project import ManagerProject
from app.utils import Warp
from algorithm import CovEntry
from sqlalchemy.exc import SQLAlchemyError
from app.models.errors import ProjectNotFound, CoverageNotExist, GitFetchError, ConcurrencyError
from app.models.manager_coverage import ManagerCoverage

ctr_coverage = Blueprint('coverage', __name__)


class CtrCoverage(MethodView):
    def post(self):
        project_id = request.json.get('project_id')
        if project_id is None or project_id == '':
            current_app.logger.error('project_id must exist', str({'project_id': project_id}))
            return Warp.fail_warp(301, 'project_id must exist')
        try:
            commit_cov = ManagerCoverage().get_commit_coverage(project_id)
            return Warp.success_warp(commit_cov)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except ProjectNotFound as e:
            current_app.logger.error(e)
            return Warp.fail_warp(302, '项目不存在')
        except CoverageNotExist as e:
            current_app.logger.error(e)
            return Warp.fail_warp(302, '项目类型覆盖率不存在')
        except ConcurrencyError as e:
            return Warp.fail_warp(503, str(e.args[0]))
        except Exception as e:
            print(e)
            return Warp.fail_warp(500, '未知错误')

    def get(self, project_id):
        if project_id is None:
            try:
                res = ManagerCoverage().get_all_coverage()
                return Warp.success_warp(res.__dict__)
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目不存在')
            except CoverageNotExist as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目类型覆盖率不存在')
            except GitFetchError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, 'Project Git Fetch Failed')
        else:
            try:
                res = ManagerCoverage().get_project_coverage(project_id)
                return Warp.success_warp(res)
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return Warp.fail_warp(501)
            except ProjectNotFound as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目不存在')
            except CoverageNotExist as e:
                current_app.logger.error(e)
                return Warp.fail_warp(302, '项目类型覆盖率不存在')
            except ConcurrencyError as e:
                return Warp.fail_warp(503, str(e.args[0]))
            except Exception as e:
                print(e)
                return Warp.fail_warp(500, '未知错误')


coverage_view = CtrCoverage.as_view('proj_coverage')
ctr_coverage.add_url_rule('/coverage', view_func=coverage_view, methods=['POST'])
ctr_coverage.add_url_rule('/coverage', defaults={'project_id': None}, view_func=coverage_view, methods=['GET'])
ctr_coverage.add_url_rule('/coverage/<int:project_id>', view_func=coverage_view, methods=['GET'])
