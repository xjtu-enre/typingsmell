import ast
from ast import ClassDef, Name, FunctionDef
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Set

from asttokens import asttokens

from algorithm.profiler.ScopedVisitor import ScopedVisitor
from algorithm.profiler.TypedEntity import TypedEntity, ComplexPattern, EntityType


class ClassRel(Enum):
    ImplicitImpl = 0
    ExplicitImpl = 1
    NoRelation = 2


class Structural:
    def __init__(self, node: ClassDef, tokens: asttokens.ASTTokens, rel_class_path: Tuple, rel_file_path: Path):
        self._class_name = node.name
        self.bases = set()
        self.method_set = set()
        self.abstract_method_set = set()
        self.rel_path: Tuple = rel_class_path
        self.rel_file_path = rel_file_path
        self.lineno = node.lineno
        self.end_lineno = node.end_lineno
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                decorator_text = tokens.get_text(stmt.decorator_list)
                self.method_set.add(stmt.name)

        for base in node.bases:
            self.bases.add(tokens.get_text(base))

    def add_method(self, method: str):
        self.method_set.add(method)

    def structural_name(self):
        return self._class_name

    def relation_with(self, rhs: 'Structural') -> ClassRel:
        if self._class_name in rhs.bases:
            return ClassRel.ExplicitImpl
        for method in self.method_set:
            if method not in rhs.method_set:
                return ClassRel.NoRelation
        if len(self.method_set) != 0:
            return ClassRel.ImplicitImpl
        else:
            return ClassRel.NoRelation

    def __str__(self):
        ret = str(self.rel_file_path)
        for e in self.rel_path:
            ret += "::" + str(e)
        return ret


class ProtocolCounterSingle(ast.NodeVisitor):
    def __init__(self, tokens: asttokens.ASTTokens, rel_path):
        self.tokens = tokens
        self.protocol_num = 0
        self.protocol_impl_implicit: int = 0
        self.protocol_impl_explicit: int = 0
        self.protocols: Set[Structural] = set()
        self.class_defs: Set[Structural] = set()
        self.implicit_impls = set()
        self.explicit_impls = set()
        self.rel_file_path = rel_path
        # self.root = root
        # self.file_path = file_path
        self.nested_scope = []

    def visit_ClassDef(self, node: ClassDef):
        self.nested_scope.append(node.name)
        is_protocol = False
        for base in node.bases:
            type_text = self.tokens.get_text(base)
            if "Protocol" in type_text:
                self.protocols.add(Structural(node, self.tokens, tuple(self.nested_scope), self.rel_file_path))
                is_protocol = True
                break
        if not is_protocol:
            self.class_defs.add(Structural(node, self.tokens, tuple(self.nested_scope), self.rel_file_path))
        self.generic_visit(node)
        self.nested_scope.pop()

    def visit_FunctionDef(self, node: FunctionDef):
        self.nested_scope.append(node.name)
        self.generic_visit(node)
        self.nested_scope.pop()

    def workflow(self):
        self.collectClass()
        self.countRelation()

    def collectClass(self):
        self.visit(self.tokens.tree)

    def countRelation(self):
        self.protocol_num = len(self.protocols)
        new_protocols: List[Structural] = []
        for structural in self.protocols:
            for class_def in self.class_defs:
                relation = structural.relation_with(class_def)
                if relation == ClassRel.ExplicitImpl:
                    new_protocols.append(class_def)
                    self.explicit_impls.add(class_def)
                    self.protocol_impl_explicit += 1
                elif relation == ClassRel.ImplicitImpl:
                    new_protocols.append(class_def)
                    self.implicit_impls.add(class_def)
                    self.protocol_impl_implicit += 1

        # for protocol in new_protocols:
        #     self.protocols.add(protocol)
        #
        # if len(new_protocols) != 0:
        #     self.countRelation()


def inherited_by(class_def: ClassDef, stub_classes: List[ClassDef]) -> bool:
    res = False
    for class_def_1 in stub_classes:
        for base in class_def_1.bases:
            if isinstance(base, Name) and base.id == class_def.name:
                res = True
                break
        if res:
            break
    return res


def get_base_presentation(src_path: Path, stub_path: Path) -> List[TypedEntity]:
    src_classes = get_classes(src_path)
    stub_classes = get_classes(stub_path)
    unmatched = unmatched_classes(src_classes, stub_classes)
    res: List[TypedEntity] = []
    for entity, class_def in unmatched:
        if inherited_by(class_def, [t[1] for t in stub_classes]):
            res.append(entity)
    with open(stub_path, "r", encoding="utf-8") as file:
        tokens = asttokens.ASTTokens(file.read(), parse=True)
        protocolCounter = ProtocolCounterSingle(tokens, stub_path)
        protocolCounter.workflow()
        for protocol in protocolCounter.protocols:
            is_new_protocol = True
            for e in res:
                if e.scope == protocol.rel_path:
                    is_new_protocol = False
            if is_new_protocol:
                res.append(
                    TypedEntity(EntityType.Class, stub_path, protocol.rel_path, protocol.lineno, protocol.end_lineno,
                                ComplexPattern.BaseClass))

    return res


def get_classes(file_path: Path) -> List[Tuple[TypedEntity, ClassDef]]:
    class GetClassVisitor(ScopedVisitor):
        def __init__(self, file_path: Path):
            super().__init__()
            self.class_entities: List[Tuple[TypedEntity, ClassDef]] = []
            self.file_path = file_path

        def visit_ClassDef(self, node: ClassDef):
            self.class_entities.append((
                TypedEntity(EntityType.Class, self.file_path, tuple(self.scope), node.lineno, node.end_lineno,
                            ComplexPattern.BaseClass),
                node))
            self.generic_visit(node)

    visitor = GetClassVisitor(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    visitor.visit(tree)
    return visitor.class_entities


def unmatched_classes(src_classes: List[Tuple[TypedEntity, ClassDef]],
                      stub_classes: List[Tuple[TypedEntity, ClassDef]]) -> List[Tuple[TypedEntity, ClassDef]]:
    res = []

    for stub_entity, stub_def in stub_classes:
        src_matched_classes = [src_entity for src_entity, src_def in src_classes if
                               src_entity.scope == stub_entity.scope]
        if len(src_matched_classes) == 0:
            res.append((stub_entity, stub_def))

    return res
