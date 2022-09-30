import os
import csv
from typing import Dict
from collections import defaultdict
from functools import partial
from app.models.errors import ProjectNotFound, PatternNotExist, ConcurrencyError
from app.utils import TypingTrans, DealFile
from app.daos.model import Pattern
from app.daos.pattern import DaoPattern
from app.daos.project import DaoProject
from app.models.modify_pattern import modify_pattern
from app.models.modify_project import modify_project
from algorithm.pratice import Pattern as ALGPattern


class PatternInfoData:
    def __init__(self, api_visibility, extension_typing, overload, typing_compatibility, functional_variable,
                 baseclass_presentation, matched_overload, new_protocol, new_protocol_impl_explicit,
                 new_protocol_impl_implicit, explicit_sub_classes, protocol_use, protocol_implicit_impl,
                 protocol_explicit_impl):
        self.ApiVisibility = api_visibility
        self.ExtensionTyping = extension_typing
        self.Overload = overload
        self.TypingCompatibility = typing_compatibility
        self.FunctionalVariable = functional_variable
        self.BaseclassPresentation = baseclass_presentation
        self.MatchedOverload = matched_overload
        self.NewProtocol = new_protocol
        self.NewProtocolImplExplicit = new_protocol_impl_explicit
        self.NewProtocolImplImplicit = new_protocol_impl_implicit
        self.ExplicitSubClasses = explicit_sub_classes
        self.ProtocolUse = protocol_use
        self.ProtocolImplicitImpl = protocol_implicit_impl
        self.ProtocolExplicitImpl = protocol_explicit_impl


def format_pattern(pattern: Pattern):
    return PatternInfoData(pattern.ApiVisibility, pattern.ExtensionTyping, pattern.Overload,
                           pattern.TypingCompatibility, pattern.FunctionalVariable,
                           pattern.BaseclassPresentation, pattern.MatchedOverload,
                           pattern.NewProtocol, pattern.NewProtocolImplExplicit,
                           pattern.NewProtocolImplImplicit, pattern.ExplicitSubClasses,
                           pattern.ProtocolUse, pattern.ProtocolImplicitImpl,
                           pattern.ProtocolExplicitImpl)


class PatternRes:
    def __init__(self, res, metrics, count):
        self.res = res
        self.metrics = metrics
        self.count = count


class IManagerPattern:
    _project: DaoProject
    _manager: DaoPattern

    def __init__(self):
        self._project = DaoProject()
        self._manager = DaoPattern()

    def add_pattern(self, project_id: int, api_visibility: int, extension_typing: int, matched_overload: int,
                    overload: int, typing_compatibility: int, functional_variable: int, baseclass_presentation: int,
                    new_protocol: int, new_protocol_impl_explicit: int, new_protocol_impl_implicit: int,
                    explicit_sub_classes: int, protocol_use: int, protocol_implicit_impl: int,
                    protocol_explicit_impl: int) -> None:
        raise NotImplementedError()

    def get_project_pattern(self, project_id):
        raise NotImplementedError()

    def get_all_pattern(self) -> PatternRes:
        raise NotImplementedError()

    def cal_pattern(self, project, stub):
        raise NotImplementedError()

    def re_cal_pattern(self, project, pattern, stub):
        raise NotImplementedError()

    def get_pattern(self, project, stub):
        raise NotImplementedError()


class ManagerPattern(IManagerPattern):
    def add_pattern(self, project_id: int, api_visibility: int, extension_typing: int, matched_overload: int,
                    overload: int, typing_compatibility: int, functional_variable: int, baseclass_presentation: int,
                    new_protocol: int, new_protocol_impl_explicit: int, new_protocol_impl_implicit: int,
                    explicit_sub_classes: int, protocol_use: int, protocol_implicit_impl: int,
                    protocol_explicit_impl: int) -> None:
        self._manager.add_pattern(project_id, api_visibility, extension_typing, matched_overload,
                                  overload, typing_compatibility, functional_variable, baseclass_presentation,
                                  new_protocol, new_protocol_impl_explicit, new_protocol_impl_implicit,
                                  explicit_sub_classes, protocol_use, protocol_implicit_impl, protocol_explicit_impl)
        return

    def get_project_pattern(self, project_id):
        project = self._project.query_project_by_id(project_id)
        if project is None:
            raise ProjectNotFound('项目不存在')
        # if project.encode_name is None or project.encode_name == '':
        #     if project.code_url != '':  # !!!!
        #         project_path, project_name, encode_project_name = DealFile().git_fetch(project.code_url)
        #         modify_project(project, {"encode_name": encode_project_name})
        #     else:
        #         raise PatternNotExist('Pattern Not Exist')
        if project.encode_name is None or project.encode_name == '':
            raise ConcurrencyError("项目可能未导入或未完成clone!")
        pattern_count, pattern_info = self.get_pattern(project, project.encode_name)
        return pattern_count, pattern_info

    def get_all_pattern(self) -> PatternRes:
        pattern_list, metrics, count = self._manager.get_pattern_list()
        return PatternRes(pattern_list, metrics, count)

    def cal_pattern(self, project, stub):
        pattern, pattern_info = ALGPattern().get_pattern(project.encode_name, stub)
        metrics = self._manager.get_pattern_metrics()
        pattern_param, other_pattern = TypingTrans().dict_to_list(metrics, pattern.__dict__)
        self.add_pattern(project.id, *pattern_param)
        return pattern.__dict__, pattern_info.__dict__

    def re_cal_pattern(self, project, pattern, stub):
        pattern_count, pattern_info = ALGPattern().get_pattern(project.encode_name, stub)
        modify_pattern(pattern, pattern_count.__dict__)
        return pattern_count.__dict__, pattern_info.__dict__

    def get_pattern(self, project, stub):
        pattern = self._manager.query_pattern_by_project(project.id)
        if pattern is None:
            if DealFile().get_cal_steps(project.encode_name) == 1 and DealFile().get_running(project.encode_name):
                raise ConcurrencyError("该项目正在进行Pattern分析!")
            pattern_count, pattern_info = self.cal_pattern(project, stub)
        else:
            pattern_count_file = "./assets/calculation/" + project.encode_name + '/PatternCount.csv'
            pattern_info_file = "./assets/calculation/" + project.encode_name + '/TypingPatterns.csv'
            if os.path.exists(pattern_count_file) and os.path.exists(pattern_info_file):
                pattern_count = format_pattern(pattern).__dict__
                pattern_info = defaultdict(partial(defaultdict, list))
                with open(pattern_info_file, 'r', encoding='utf-8') as f:
                    for entity in csv.reader(f):
                        pattern_info[entity[1]][entity[2]].append(
                            {'entity_type': entity[3], 'start_line': entity[4], 'end_line': entity[5]})

            else:
                pattern_count, pattern_info = self.re_cal_pattern(project, pattern, stub)

        return pattern_count, pattern_info
