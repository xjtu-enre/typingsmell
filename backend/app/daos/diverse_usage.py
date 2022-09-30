from app.daos import db, session_commit
from app.daos.model import Project, DiverseUsage
from app.daos.project import DaoProject
from typing import List, Dict, Any
from app.models.errors import UsageNotExist


class UsageInfoData:
    def __init__(self, project_name, type_optional, type_any, type_list, type_union, type_dict, type_tuple, type_type,
                 type_callable, type_mutable_mapping, type_sequence, type_iterable, type_set, type_mapping,
                 type_others):
        self.project_name = project_name
        self.Optional = type_optional
        self.Any = type_any
        self.List = type_list
        self.Union = type_union
        self.Dict = type_dict
        self.Tuple = type_tuple
        self.Type = type_type
        self.Callable = type_callable
        self.MutableMapping = type_mutable_mapping
        self.Sequence = type_sequence
        self.Iterable = type_iterable
        self.Set = type_set
        self.Mapping = type_mapping
        self.Others = type_others


class UsageListData:
    def __init__(self, project_id, project_name, type_optional, type_any, type_list, type_union, type_dict, type_tuple,
                 type_type, type_callable, type_mutable_mapping, type_sequence, type_iterable, type_set, type_mapping,
                 type_others):
        self.project_id = project_id
        self.usage = UsageInfoData(project_name, type_optional, type_any, type_list, type_union, type_dict,
                                   type_tuple, type_type, type_callable, type_mutable_mapping, type_sequence,
                                   type_iterable, type_set, type_mapping, type_others).__dict__


class IUsage:
    metrics = ['Optional', 'Any', 'List', 'Union', 'Dict', 'Tuple',
               'Type', 'Callable', 'MutableMapping', 'Sequence', 'Iterable', 'Set',
               'Mapping', 'Others']

    def query_usage_by_id(self, uid: int) -> DiverseUsage:
        raise NotImplementedError()

    def query_usage_by_project(self, pid: int) -> DiverseUsage:
        raise NotImplementedError()

    def add_usage(self, project_id: int, type_optional: int = 0, type_any: int = 0, type_list: int = 0,
                  type_union: int = 0, type_dict: int = 0, type_tuple: int = 0, type_type: int = 0,
                  type_callable: int = 0, type_mutable_mapping: int = 0, type_sequence: int = 0, type_iterable: int = 0,
                  type_set: int = 0, type_mapping: int = 0, type_others: int = 0) -> None:
        raise NotImplementedError()

    def modify_usage(self, usage: DiverseUsage, type_optional: int = 0, type_any: int = 0, type_list: int = 0,
                     type_union: int = 0, type_dict: int = 0, type_tuple: int = 0, type_type: int = 0,
                     type_callable: int = 0, type_mutable_mapping: int = 0, type_sequence: int = 0,
                     type_iterable: int = 0, type_set: int = 0, type_mapping: int = 0, type_others: int = 0) -> None:
        raise NotImplementedError()

    def get_usage_list(self) -> (List[Dict[str, Any]], List[str], int):
        raise NotImplementedError()

    def get_usage_metric(self) -> List:
        raise NotImplementedError()


class DaoUsage(IUsage):
    def query_usage_by_id(self, uid: int) -> DiverseUsage:
        return DiverseUsage.query. \
            filter_by(id=uid). \
            first()

    def query_usage_by_project(self, pid: int) -> DiverseUsage:
        return DiverseUsage.query.filter_by(project_id=pid).first()

    def add_usage(self, project_id: int, type_optional: int = 0, type_any: int = 0, type_list: int = 0,
                  type_union: int = 0, type_dict: int = 0, type_tuple: int = 0, type_type: int = 0,
                  type_callable: int = 0, type_mutable_mapping: int = 0, type_sequence: int = 0, type_iterable: int = 0,
                  type_set: int = 0, type_mapping: int = 0, type_others: int = 0) -> None:
        usage = DiverseUsage(project_id=project_id, Optional=type_optional, Any=type_any, List=type_list,
                             Union=type_union, Dict=type_dict, Tuple=type_tuple, Type=type_type,
                             Callable=type_callable, MutableMapping=type_mutable_mapping, Sequence=type_sequence,
                             Iterable=type_iterable, Set=type_set, Mapping=type_mapping, Others=type_others)
        db.session.add(usage)
        session_commit()

    def modify_usage(self, usage: DiverseUsage, type_optional: int = 0, type_any: int = 0, type_list: int = 0,
                     type_union: int = 0, type_dict: int = 0, type_tuple: int = 0, type_type: int = 0,
                     type_callable: int = 0, type_mutable_mapping: int = 0, type_sequence: int = 0,
                     type_iterable: int = 0, type_set: int = 0, type_mapping: int = 0, type_others: int = 0) -> None:
        usage.Optional = type_optional
        usage.Any = type_any
        usage.List = type_list
        usage.Union = type_union
        usage.Dict = type_dict
        usage.Tuple = type_tuple
        usage.Type = type_type
        usage.Callable = type_callable
        usage.MutableMapping = type_mutable_mapping
        usage.Sequence = type_sequence
        usage.Iterable = type_iterable
        usage.Set = type_set
        usage.Mapping = type_mapping
        usage.Others = type_others
        session_commit()

    def get_usage_list(self) -> (List[Dict[str, Any]], List[str], int):
        sql = DiverseUsage.query. \
            filter_by(delete_at=None)
        temp = sql.all()
        count = sql.count()
        usage_list: List[Dict[str, Any]] = []
        for item in temp:
            project = DaoProject().query_project_by_id(item.project_id)
            if project is not None:
                usage_list.append(
                    UsageListData(item.project_id, project.name, item.Optional, item.Any, item.List, item.Union,
                                  item.Dict, item.Tuple, item.Type, item.Callable, item.MutableMapping, item.Sequence,
                                  item.Iterable, item.Set, item.Mapping, item.Others).__dict__)
        metrics = self.metrics
        return usage_list, metrics, count

    def get_usage_metric(self) -> List:
        return self.metrics
