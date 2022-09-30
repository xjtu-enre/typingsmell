import csv
import os
import time
from flask import Blueprint, request, current_app
from flask.views import MethodView

from app.daos.project import DaoProject
from app.models.modify_project import modify_project
from app.utils import Warp, DealFile
from sqlalchemy.exc import SQLAlchemyError
from app.models.errors import NetWorkError, EnreRunError, GitFetchError, GitCheckoutError, GitRepoNotExist, \
    ConcurrencyError
from app.models.manager_files import ManagerFile
from app.models.manager_coverage import ManagerCoverage
from app.models.manager_usage import ManagerUsage
from app.models.manager_pattern import ManagerPattern
from algorithm.pratice import Tool

import_project = Blueprint('import_project', __name__, url_prefix='/project')


class Analysis(MethodView):
    def post(self):
        if 'file' in request.files:
            csvfile = request.files['file']
            upload_time = time.time()
            to_path = f"./assets/uploads/{int(upload_time)}{csvfile.filename}"
            csvfile.save(to_path)
            try:
                with open(to_path, 'r', encoding='utf-8') as f:
                    for entity in csv.DictReader(f):
                        url = entity['url']
                        try:
                            git_source, git_url = DealFile().git_url_deal(url)
                        except GitRepoNotExist:
                            print(f"无法识别的链接:{url}")
                            continue
                        self.__import_by_url(git_source, git_url)
            except UnicodeDecodeError:
                return Warp.fail_warp(400, "Please upload csv file!")
            except KeyError:
                return Warp.fail_warp(400, "Please check whether the \'url\' column is included!")
            finally:
                os.remove(to_path)
            return Warp.success_warp({"succ": f"{csvfile.filename} import over."})
        else:
            git_source = request.json.get('git_source')
            git_url = request.json.get('git_url')
            if git_url is None or git_url == '':
                current_app.logger.error('项目url不能为空', str({'git_url': git_url}))
                return Warp.fail_warp(301, '项目名url不能为空')
            return self.__import_by_url(git_source, git_url)

    @staticmethod
    def __import_by_url(git_source, git_url):
        running_project = ""
        try:
            project = ManagerFile().fetch_project(git_source, git_url)
            DealFile().status_signal(project.encode_name, 1, "clone over!")
            running_project = project.encode_name
            DealFile().set_running(running_project, True)
            coverage = ManagerCoverage().get_coverage(project, project.encode_name)
            DealFile().status_signal(project.encode_name, 2, "coverage analysis over!")
            usage = ManagerUsage().get_usage(project, project.encode_name)
            DealFile().status_signal(project.encode_name, 3, "diverse types'usage analysis over!")
            pattern_count, pattern_info = ManagerPattern().get_pattern(project, project.encode_name)
            DealFile().status_signal(project.encode_name, 4, "type patterns analysis over!")
            Tool().use_enre(project.encode_name)
            print("调用enre-type分析完成！")
            ManagerCoverage().get_commit_coverage(project.id)
            DealFile().status_signal(project.encode_name, -1, "coverage timeline analysis over!")
            DealFile().set_running(project.encode_name, False)
            return
            # return Warp.success_warp(
            #     {'cov': coverage, 'usage': usage, 'pattern': pattern_count, 'pattern_info': pattern_info})
        except NetWorkError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(503, '服务器网络错误')
        except EnreRunError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(503, '依赖抽取错误')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(501)
        except GitFetchError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(512, 'gitclone错误')
        except GitCheckoutError as e:
            current_app.logger.error(e)
            return Warp.fail_warp(513, 'checkout错误')
        except ConcurrencyError as e:
            return Warp.fail_warp(503, str(e.args[0]))
        except Exception as e:
            print(e)
            return Warp.fail_warp(500, '未知错误')
        finally:
            if running_project is not "":
                DealFile().set_running(running_project, False)


fetch_view = Analysis.as_view('import_project')

import_project.add_url_rule('/import', view_func=fetch_view, methods=['POST'])
