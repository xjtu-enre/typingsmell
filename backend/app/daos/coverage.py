from app.daos import db, session_commit
from app.daos.model import Coverage
from app.daos.project import DaoProject
from typing import List, Dict, Any


class CoverageInfoData:
    def __init__(self, project_name, file, func, loc, var):
        self.project_name = project_name
        self.file = file
        self.func = func
        self.loc = loc
        self.var = var


class CoverageListData:
    def __init__(self, project_id, project_name, file, func, loc, var):
        self.project_id = project_id
        self.coverage = CoverageInfoData(project_name, file, func, loc, var).__dict__


class ICoverage:
    metrics = ['file', 'func', 'loc', 'var']

    def query_coverage_by_id(self, cid: int) -> Coverage:
        raise NotImplementedError()

    def query_coverage_by_project(self, pid: int) -> Coverage:
        raise NotImplementedError()

    def add_coverage(self, project_id: int, file: float, func: float, loc: float, var: float) -> None:
        raise NotImplementedError()

    def modify_coverage(self, coverage: Coverage, file: float, func: float, loc: float, var: float) -> None:
        raise NotImplementedError()

    def get_coverage_list(self) -> (List[Dict[str, Any]], List[str], int):
        raise NotImplementedError()

    def get_coverage_metric(self) -> List:
        raise NotImplementedError()


class DaoCoverage(ICoverage):
    def query_coverage_by_id(self, cid: int) -> Coverage:
        return Coverage.query. \
            filter_by(id=cid). \
            first()

    def query_coverage_by_project(self, pid: int) -> Coverage:
        return Coverage.query.filter_by(project_id=pid).first()
        # if sql is None:
        #     raise CoverageNotExist('项目类型覆盖率不存在')
        # return CoverageInfoData(sql.loc, sql.file, sql.func, sql.var).__dict__

    def add_coverage(self, project_id: int, file: float, func: float, loc: float, var: float) -> None:
        coverage = Coverage(project_id=project_id, file=file, func=func, loc=loc, var=var)
        db.session.add(coverage)
        session_commit()

    def modify_coverage(self, coverage: Coverage, file: float, func: float, loc: float, var: float) -> None:
        coverage.file = file
        coverage.func = func
        coverage.loc = loc
        coverage.var = var
        session_commit()

    def get_coverage_list(self) -> (List[Dict[str, Any]], List[str], int):
        sql = Coverage.query. \
            filter_by(delete_at=None)
        temp = sql.all()
        count = sql.count()
        coverage_list: List[Dict[str, Any]] = []
        for item in temp:
            project = DaoProject().query_project_by_id(item.project_id)
            if project is not None:
                coverage_list.append(
                    CoverageListData(project_id=item.project_id, project_name=project.name, file=item.file,
                                     func=item.func, loc=item.loc, var=item.var).__dict__)
        metrics = ['file', 'func', 'loc', 'var']
        return coverage_list, metrics, count

    def get_coverage_metric(self) -> List:
        return self.metrics
