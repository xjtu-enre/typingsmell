import os.path
import shutil
import warnings

from app.models.errors import ProjectNotFound, ProjectHasExist
from app.daos.project import DaoProject


class ProjectListRes:
    def __init__(self, res, count, fin_count):
        self.res = res
        self.count = count
        self.fin = fin_count


class IManagerProject:
    _project_id: int
    _page: int
    _limit: int
    _manager: DaoProject
    _kwds: str

    def __init__(self, project_id=0, page=0, limit=10, kwds=''):
        self._project_id = project_id
        self._page = page
        self._limit = limit
        self._kwds = kwds
        self._manager = DaoProject()

    def add_project(self, project_name: str, encode_name: str, file: int = 0, loc: int = 0, version: str = '',
                    type_manner: str = '', code_url='', star='0') -> None:
        raise NotImplementedError()

    def delete_project(self) -> None:
        raise NotImplementedError()

    def get_all_project(self) -> ProjectListRes:
        raise NotImplementedError()


class ManagerProject(IManagerProject):
    def add_project(self, project_name: str, encode_name: str, file: int = 0, loc: int = 0, version: str = '',
                    type_manner: str = '', code_url='', star='0') -> None:
        warnings.warn("禁用本地上传项目功能", DeprecationWarning)
        self._manager.add_project(project_name, encode_name, file, loc, version, type_manner, code_url, star)
        return

    def delete_project(self) -> None:
        project = self._manager.query_project_by_id(self._project_id)
        if project is None:
            raise ProjectNotFound('项目不存在')
        self._manager.delete_project(project)
        p_dir = "./assets/projects/" + project.encode_name
        if os.path.exists(p_dir):
            shutil.rmtree(p_dir)

    def get_all_project(self) -> ProjectListRes:
        project_list, count, fin_count = self._manager.get_project_list(self._page, self._limit, self._kwds)
        return ProjectListRes(project_list, count, fin_count)
