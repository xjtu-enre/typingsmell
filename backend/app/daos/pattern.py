from app.daos import db, session_commit
from app.daos.model import Pattern
from app.daos.project import DaoProject
from typing import List, Dict, Any


class PatternListData:
    def __init__(self, project_id, project_name, api_visibility, extension_typing, matched_overload,
                 overload, typing_compatibility, functional_variable, baseclass_presentation, new_protocol,
                 new_protocol_impl_explicit, new_protocol_impl_implicit, explicit_sub_classes,
                 protocol_use, protocol_implicit_impl, protocol_explicit_impl):
        self.project_id = project_id
        self.project_name = project_name
        self.ApiVisibility = api_visibility
        self.ExtensionTyping = extension_typing
        self.MatchedOverload = matched_overload
        self.Overload = overload
        self.TypingCompatibility = typing_compatibility
        self.FunctionalVariable = functional_variable
        self.BaseclassPresentation = baseclass_presentation
        self.NewProtocol = new_protocol
        self.NewProtocolImplExplicit = new_protocol_impl_explicit
        self.NewProtocolImplImplicit = new_protocol_impl_implicit
        self.ExplicitSubClasses = explicit_sub_classes
        self.ProtocolUse = protocol_use
        self.ProtocolImplicitImpl = protocol_implicit_impl
        self.ProtocolExplicitImpl = protocol_explicit_impl


class IPattern:
    metrics = ['ApiVisibility', 'ExtensionTyping', 'MatchedOverload',
               'Overload', 'TypingCompatibility', 'FunctionalVariable',
               'BaseclassPresentation', 'NewProtocol', 'NewProtocolImplExplicit',
               'NewProtocolImplImplicit', 'ExplicitSubClasses', 'ProtocolUse',
               'ProtocolImplicitImpl', 'ProtocolExplicitImpl']

    def get_pattern_metrics(self) -> List:
        raise NotImplementedError()

    def query_pattern_by_id(self, tid: int) -> Pattern:
        raise NotImplementedError()

    def query_pattern_by_project(self, pid: int) -> Pattern:
        raise NotImplementedError()

    def add_pattern(self, project_id: int, api_visibility: int, extension_typing: int, matched_overload: int,
                    overload: int, typing_compatibility: int, functional_variable: int, baseclass_presentation: int,
                    new_protocol: int, new_protocol_impl_explicit: int, new_protocol_impl_implicit: int,
                    explicit_sub_classes: int, protocol_use: int, protocol_implicit_impl: int,
                    protocol_explicit_impl: int) -> None:
        raise NotImplementedError()

    def get_pattern_list(self) -> (List[Dict[str, Any]], List[str], int):
        raise NotImplementedError()


class DaoPattern(IPattern):
    def get_pattern_metrics(self) -> List:
        return self.metrics

    def query_pattern_by_id(self, tid: int) -> Pattern:
        return Pattern.query. \
            filter_by(id=tid). \
            first()

    def query_pattern_by_project(self, pid: int) -> Pattern:
        return Pattern.query. \
            filter_by(project_id=pid). \
            first()

    def add_pattern(self, project_id: int, api_visibility: int, extension_typing: int, matched_overload: int,
                    overload: int, typing_compatibility: int, functional_variable: int, baseclass_presentation: int,
                    new_protocol: int, new_protocol_impl_explicit: int, new_protocol_impl_implicit: int,
                    explicit_sub_classes: int, protocol_use: int, protocol_implicit_impl: int,
                    protocol_explicit_impl: int) -> None:
        pattern = Pattern(project_id=project_id, ApiVisibility=api_visibility, ExtensionTyping=extension_typing,
                          MatchedOverload=matched_overload, Overload=overload,
                          TypingCompatibility=typing_compatibility, FunctionalVariable=functional_variable,
                          BaseclassPresentation=baseclass_presentation, NewProtocol=new_protocol,
                          NewProtocolImplExplicit=new_protocol_impl_explicit,
                          NewProtocolImplImplicit=new_protocol_impl_implicit,
                          ExplicitSubClasses=explicit_sub_classes, ProtocolUse=protocol_use,
                          ProtocolImplicitImpl=protocol_implicit_impl, ProtocolExplicitImpl=protocol_explicit_impl)
        db.session.add(pattern)
        session_commit()

    def get_pattern_list(self) -> (List[Dict[str, Any]], List[str], int):
        sql = Pattern.query. \
            filter_by(delete_at=None)
        temp = sql.all()
        count = sql.count()
        pattern_list: List[Dict[str, Any]] = []
        for item in temp:
            project = DaoProject().query_project_by_id(item.project_id)
            if project is not None:
                pattern_list.append(
                    PatternListData(project.id, project.name, item.ApiVisibility, item.ExtensionTyping,
                                    item.MatchedOverload, item.Overload, item.TypingCompatibility,
                                    item.FunctionalVariable, item.BaseclassPresentation, item.NewProtocol,
                                    item.NewProtocolImplExplicit, item.NewProtocolImplImplicit, item.ExplicitSubClasses,
                                    item.ProtocolUse, item.ProtocolImplicitImpl, item.ProtocolExplicitImpl).__dict__)

        return pattern_list, self.metrics, count
