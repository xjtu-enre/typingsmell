import ast
from _ast import If, Attribute
from ast import NodeVisitor, Import, ClassDef, ImportFrom
from pathlib import Path
from typing import Any, List

from algorithm.profiler.ScopedVisitor import ScopedVisitor
from algorithm.profiler.TypedEntity import TypedEntity, EntityType, ComplexPattern


def has_version_judge(test) -> bool:
    class HasVersionJudge(NodeVisitor):
        def __init__(self):
            self.has_version_judge_indicator = False

        def visit_Attribute(self, node: Attribute) -> Any:
            if node.attr == "version_info":
                self.has_version_judge_indicator = True
                return
            self.generic_visit(node)

    visitor = HasVersionJudge()
    visitor.visit(test)
    return visitor.has_version_judge_indicator


def have_typing_import(stmts) -> bool:
    class HasTypingImport(NodeVisitor):
        def __init__(self):
            self.has_typing_import_indicator = False

        def visit_Import(self, node: Import) -> Any:
            for alias in node.names:
                if alias.name == "typing":
                    self.has_typing_import_indicator = True
                    return
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ImportFrom) -> Any:
            if node.module is not None and node.module == "typing":
                self.has_typing_import_indicator = True
                return

    visitor = HasTypingImport()
    for stmt in stmts:
        visitor.visit(stmt)
        if visitor.has_typing_import_indicator:
            return True
    return False


def have_class_def(stmts) -> bool:
    class HasClassDef(NodeVisitor):
        def __init__(self):
            self.has_class_def = False

        def visit_ClassDef(self, node: ClassDef) -> Any:
            self.has_class_def = True

    visitor = HasClassDef()
    for stmt in stmts:
        visitor.visit(stmt)
        if visitor.has_class_def:
            return True
    return False


def is_importing_class(node, file_path):
    return True


def have_class_import(stmts, file_path: Path) -> bool:
    class GetImport(NodeVisitor):
        def __init__(self):
            self.import_stmts = []
            self.importFrom_stmts = []

        def visit_ImportFrom(self, node: ImportFrom) -> Any:
            if (is_importing_class(node, file_path)):
                self.importFrom_stmts.append(node)
            self.generic_visit(node)

        def visit_Import(self, node: Import) -> Any:
            if (is_importing_class(node, file_path)):
                self.import_stmts.append(node)
            self.generic_visit(node)

    visitor = GetImport()
    for stmt in stmts:
        visitor.visit(stmt)
        if len(visitor.import_stmts) != 0:
            return True
        if len(visitor.importFrom_stmts) != 0:
            return True
    return False


class VersionCompProfiler(ScopedVisitor):
    def __init__(self, file_path: Path):
        super().__init__()
        self.version_compatible_usage: List[TypedEntity] = []
        self.file_path: Path = file_path

    def register_an_entity(self, entity: TypedEntity):
        self.version_compatible_usage.append(entity)

    def visit_If(self, node: If) -> Any:
        if has_version_judge(node.test):
            if (have_typing_import(node.body) and (
                    have_class_def(node.orelse) or have_class_import(node.orelse, self.file_path))) or (
                    have_typing_import(node.orelse) and (
                    have_class_def(node.body) or have_class_import(node.body, self.file_path))):
                entity = TypedEntity(EntityType.IfStmt, self.file_path, tuple(self.scope), node.lineno, node.end_lineno,
                                     ComplexPattern.TypeCompatibility)
                self.register_an_entity(entity)
        self.generic_visit(node)


def get_version_comp_pattern_usage(file_path: Path) -> List[TypedEntity]:
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read())
        except:
            return []
        has_version_C_visitor = VersionCompProfiler(file_path)
        has_version_C_visitor.visit(tree)
        return has_version_C_visitor.version_compatible_usage
