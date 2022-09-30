import datetime
import warnings

from sqlalchemy import or_

from app.daos import db, session_commit
from app.daos.model import Project
from app.utils import FormatTime, DealFile
from typing import List, Dict, Any


class ProjectInfoData:
    def __init__(self, pid, project_name, create_at, version, file, loc, type_manner, git_url, star, step):
        self.id = pid
        self.project_name = project_name
        self.create_at = create_at
        self.version = version
        self.file = file
        self.loc = loc
        self.type_manner = type_manner
        self.git_url = git_url
        self.star = star
        self.step = step


class IProject:
    def query_project_by_id(self, pid: int) -> Project:
        raise NotImplementedError()

    def query_projects_by_keyword(self, kwds: str) -> (List[Project], int):
        raise NotImplementedError()

    def query_project_by_encode_name(self, name: str) -> Project:
        raise NotImplementedError()

    def query_project_by_repository(self, name: str) -> Project:
        raise NotImplementedError()

    def add_project(self, name: str, encode_name: str = '', file: int = 0, loc: int = 0, version: str = None,
                    type_manner: str = None, code_url: str = None, star=None) -> None:
        raise NotImplementedError()

    def delete_project(self, project: Project) -> None:
        raise NotImplementedError()

    def get_project_list(self, page: int, limit: int, kwds: str) -> (List[Dict[str, Any]], int, int):
        raise NotImplementedError()


class DaoProject(IProject):
    def query_project_by_id(self, pid: int) -> Project:
        return Project.query. \
            filter_by(id=pid). \
            filter_by(delete_at=None). \
            first()

    def query_projects_by_keyword(self, kwds: str) -> (List[Project], int):
        warnings.warn("query_projects_by_keyword is deprecated", DeprecationWarning)
        sql = Project.query. \
            filter_by(delete_at=None). \
            filter(or_(Project.name.like(kwds), Project.encode_name.like(kwds)))
        count = sql.count()
        rs = sql.all()
        return rs, count

    def query_project_by_encode_name(self, name: str) -> Project:
        return Project.query. \
            filter_by(encode_name=name). \
            filter_by(delete_at=None). \
            first()

    def query_project_by_repository(self, name: str) -> Project:
        return Project.query. \
            filter_by(code_url=name). \
            filter_by(delete_at=None). \
            first()

    def add_project(self, name: str, encode_name: str = '', file: int = 0, loc: int = 0, version: str = '',
                    type_manner: str = '', code_url: str = '', star: str = '') -> None:
        project = Project(name=name, encode_name=encode_name, file=file, loc=loc, version=version,
                          type_manner=type_manner, code_url=code_url, star=star)
        db.session.add(project)
        session_commit()

    def delete_project(self, project: Project) -> None:
        project.delete_at = datetime.datetime.now()
        session_commit()

    def get_project_list(self, page: int, limit: int, kwds: str = "") -> (List[Dict[str, Any]], int, int):
        sql = Project.query. \
            filter_by(delete_at=None)
        if kwds is not None and kwds != '':
            sql = sql.filter(or_(Project.name.like(f"%{kwds}%"), Project.encode_name.like(f"%{kwds}%")))
        if limit == 0:
            temp = sql.all()
        else:
            temp = sql.limit(limit).offset(page * limit).all()
        sql_fin = sql.filter_by(step=5)
        count = sql.count()
        project_list: List[Dict[str, Any]] = []
        fin_count = sql_fin.count()
        for item in temp:
            step = DealFile().get_cal_steps(item.encode_name)
            project_list.append(
                ProjectInfoData(item.id, item.name, FormatTime.format_time(item.create_at), item.version, item.file,
                                item.loc, item.type_manner, item.code_url, item.star, step=step).__dict__)
        return project_list, count, fin_count
