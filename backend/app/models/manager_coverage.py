import os
from typing import Dict
from git import Repo
from app.models.errors import ProjectNotFound, CoverageNotExist, ConcurrencyError
from app.models.modify_project import modify_project
from app.daos.coverage import DaoCoverage
from app.daos.project import DaoProject
from app.daos.model import Coverage, Project
from algorithm.pratice import Coverage
from app.utils import DealFile


class CoverageInfoData:
    def __init__(self, file, func, loc, var):
        self.file = file
        self.func = func
        self.loc = loc
        self.var = var


class CoverageRes:
    def __init__(self, res, metrics, count):
        self.res = res
        self.metrics = metrics
        self.count = count


class IManagerCoverage:
    _project: DaoProject
    _manager: DaoCoverage

    def __init__(self):
        self._project = DaoProject()
        self._manager = DaoCoverage()

    def add_coverage(self, project_id: int, file: int, func: int, loc: int, var: int) -> None:
        raise NotImplementedError()

    def get_project_coverage(self, project_id) -> Dict:
        raise NotImplementedError()

    def get_all_coverage(self) -> CoverageRes:
        raise NotImplementedError()

    def cal_coverage(self, project, stub):
        raise NotImplementedError()

    def re_cal_coverage(self, project, coverage, stub):
        raise NotImplementedError()

    def get_coverage(self, project, stub):
        raise NotImplementedError()

    def get_commit_coverage(self, project):
        raise NotImplementedError()


class ManagerCoverage(IManagerCoverage):
    def add_coverage(self, project_id: int, file: int, func: int, loc: int, var: int) -> None:
        self._manager.add_coverage(project_id, file, func, loc, var)
        return

    def get_project_coverage(self, project_id) -> Dict:
        project = self._project.query_project_by_id(project_id)
        if project is None:
            raise ProjectNotFound('项目不存在')
        # if project.encode_name is None or project.encode_name == '':
        #     if project.code_url != '':
        #         project_path, project_name, encode_project_name = DealFile().git_fetch(project.code_url)
        #         modify_project(project, {"encode_name": encode_project_name})
        #     else:
        #         raise CoverageNotExist('Coverage Not Exist')
        if project.encode_name is None or project.encode_name == '':
            raise ConcurrencyError("项目可能未导入或未完成clone!")
        coverage_info = self.get_coverage(project, project.encode_name)
        return coverage_info

    def get_all_coverage(self) -> CoverageRes:
        coverage_list, metrics, count = self._manager.get_coverage_list()
        return CoverageRes(coverage_list, metrics, count)

    def cal_coverage(self, project, stub):
        coverage, file_num, line_count, type_manner = Coverage().get_coverage(project.encode_name, stub)
        self.add_coverage(project_id=project.id, loc=coverage.loc, file=coverage.file, func=coverage.fun,
                          var=coverage.var)
        modify_project(project, {'file': file_num, 'loc': line_count, 'type_manner': type_manner})
        return coverage.__dict__

    def re_cal_coverage(self, project, coverage, stub):
        coverage_info, file_num, line_count, type_manner = Coverage().get_coverage(project.encode_name, stub)
        self._manager.modify_coverage(coverage, file=coverage_info.file, func=coverage_info.fun, loc=coverage_info.loc,
                                      var=coverage_info.var)
        modify_project(project, {'file': file_num, 'loc': line_count, 'type_manner': type_manner})
        return coverage_info.__dict__

    def get_coverage(self, project, stub):
        coverage = self._manager.query_coverage_by_project(project.id)
        if coverage is None:
            if DealFile().get_cal_steps(project.encode_name) == 1 and DealFile().get_running(project.encode_name):
                raise ConcurrencyError("该项目正在进行Coverage分析!")
            coverage_info = self.cal_coverage(project, stub)
        else:
            if os.path.exists("./assets/calculation/" + project.encode_name + '/TypeRelatedLines.csv') is True:
                coverage_info = CoverageInfoData(coverage.file, coverage.func, coverage.loc, coverage.var).__dict__
            else:
                coverage_info = self.re_cal_coverage(project, coverage, stub)
        return coverage_info

    def get_commit_coverage(self, project_id):
        project = self._project.query_project_by_id(project_id)
        if project is None:
            raise ProjectNotFound('项目不存在')
        # if project.encode_name is None or project.encode_name == '':
        #     if project.code_url != '':
        #         project_path, project_name, encode_project_name = DealFile().git_fetch(project.code_url)
        #         modify_project(project, {"encode_name": encode_project_name})
        #     else:
        #         raise ProjectNotFound('Project Not Found')
        if project.encode_name is None or project.encode_name == '':
            raise ConcurrencyError("项目可能未导入或未完成clone!")
        commit_cov = Coverage().get_commit_coverage(project.encode_name)
        return commit_cov
