import os
from typing import Dict
from app.models.errors import ProjectNotFound, UsageNotExist, ConcurrencyError
from app.daos.model import DiverseUsage
from app.models.modify_project import modify_project
from app.daos.diverse_usage import DaoUsage
from app.daos.project import DaoProject
from app.utils import TypingTrans, DealFile
from algorithm.pratice import Pattern


class UsageInfoData:
    def __init__(self, type_optional, type_any, type_list, type_union, type_dict, type_tuple, type_type, type_callable,
                 type_mutable_mapping, type_sequence, type_iterable, type_set, type_mapping, type_others):
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


def format_usage(usage: DiverseUsage):
    return UsageInfoData(usage.Optional, usage.Any, usage.List, usage.Union, usage.Dict, usage.Tuple, usage.Type,
                         usage.Callable, usage.MutableMapping, usage.Sequence, usage.Iterable, usage.Set,
                         usage.Mapping, usage.Others)


class UsageRes:
    def __init__(self, res, metrics, count):
        self.res = res
        self.metrics = metrics
        self.count = count


class IManagerUsage:
    _project: DaoProject
    _manager: DaoUsage

    def __init__(self):
        self._project = DaoProject()
        self._manager = DaoUsage()

    def add_usage(self, project_id: int, type_optional: int, type_any: int, type_list: int, type_union: int,
                  type_dict: int, type_tuple: int, type_type: int, type_callable: int, type_mutable_mapping: int,
                  type_sequence: int, type_iterable: int, type_set: int, type_mapping: int, type_others: int) -> None:
        raise NotImplementedError()

    def get_project_usage(self, project_id) -> Dict:
        raise NotImplementedError()

    def get_all_usage(self) -> UsageRes:
        raise NotImplementedError()

    def cal_usage(self, project, stub):
        raise NotImplementedError()

    def re_cal_usage(self, project, usage, stub):
        raise NotImplementedError()

    def get_usage(self, project, stub):
        raise NotImplementedError()


class ManagerUsage(IManagerUsage):
    def add_usage(self, project_id: int, *usage) -> None:
        # type_optional: int, type_any: int, type_list: int, type_union: int,
        # type_dict: int, type_tuple: int, type_type: int, type_callable: int, type_mutable_mapping: int,
        # type_sequence: int, type_iterable: int, type_set: int, type_mapping: int, type_others: int
        self._manager.add_usage(project_id, *usage)
        return

    def get_project_usage(self, project_id) -> Dict:
        project = self._project.query_project_by_id(project_id)
        if project is None:
            raise ProjectNotFound('项目不存在')
        # if project.encode_name is None or project.encode_name == '':
        #     if project.code_url != '':  # !!!!
        #         project_path, project_name, encode_project_name = DealFile().git_fetch(project.code_url)
        #         modify_project(project, {"encode_name": encode_project_name})
        #     else:
        #         raise UsageNotExist('Usage Not Exist')
        usage_info = self.get_usage(project, project.encode_name)
        return usage_info

    def get_all_usage(self) -> UsageRes:
        usage_list, metrics, count = self._manager.get_usage_list()
        return UsageRes(usage_list, metrics, count)

    def cal_usage(self, project, stub):
        usage = Pattern().get_usage(project.encode_name, stub)
        metrics = self._manager.get_usage_metric()
        temp_metrics = metrics.copy()
        temp_metrics.pop()
        usage_param, other_usage = TypingTrans().dict_to_list(temp_metrics, usage)
        others = 0
        for key in other_usage:
            others += other_usage[key]
        usage_param.append(others)
        self.add_usage(project.id, *usage_param)
        return usage

    def re_cal_usage(self, project, usage, stub):
        usage_info = Pattern().get_usage(project.encode_name, stub)
        metrics = self._manager.get_usage_metric()
        temp_metrics = metrics.copy()
        temp_metrics.pop()
        usage_param, other_usage = TypingTrans().dict_to_list(temp_metrics, usage_info)
        others = 0
        for key in other_usage:
            others += other_usage[key]
        usage_param.append(others)
        self._manager.modify_usage(usage, *usage_param)
        return usage_info

    def get_usage(self, project, stub):
        usage = self._manager.query_usage_by_project(project.id)
        if usage is None:
            if DealFile().get_cal_steps(project.encode_name) == 0:
                raise ConcurrencyError("项目可能未导入或未完成clone!")
            elif DealFile().get_cal_steps(project.encode_name) == 1 and DealFile().get_running(project.encode_name):
                raise ConcurrencyError("该项目正在进行Usage分析!")
            usage_info = self.cal_usage(project, stub)
        else:
            if os.path.exists("./assets/calculation/" + project.encode_name + '/ImportDependency.csv') is True:
                usage_info = format_usage(usage).__dict__
            else:
                usage_info = self.re_cal_usage(project, usage, stub)
        return usage_info
