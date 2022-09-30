import ast
from ast import Assign, Import, ImportFrom, Constant, FunctionDef, AnnAssign, Name
from pathlib import Path
from typing import List, Any

from algorithm.profiler.ScopedVisitor import ScopedVisitor
from algorithm.profiler.TypedEntity import TypedEntity, EntityType, ComplexPattern


def get_api_visibility(src_file: Path, stub_file: Path) -> List[TypedEntity]:
    def get_all_assigns() -> List[Assign]:
        class GetAssign(ast.NodeVisitor):
            def __init__(self):
                self.assign_stmts = []

            def visit_Assign(self, node: Assign):
                for target in node.targets:
                    if isinstance(target, Name) and target.id == "__all__":
                        self.assign_stmts.append(node)
                self.generic_visit(node)

        visitor = GetAssign()
        visitor.visit(src_tree)
        return visitor.assign_stmts

    with open(src_file, "r", encoding="utf-8") as file:
        src_tree = ast.parse(file.read())
    with open(stub_file, "r", encoding="utf-8") as file:
        stub_tree = ast.parse(file.read())

    all_assigns = get_all_assigns()

    def is_typed_var(arg):
        class GetTypedFunVars(ScopedVisitor):
            def __init__(self):
                super().__init__()
                self.entities: List[TypedEntity] = []

            def visit_FunctionDef(self, node: FunctionDef) -> Any:
                self.entities.append(
                    TypedEntity(EntityType.Function, stub_file, tuple(self.scope), node.lineno, node.end_lineno,
                                ComplexPattern.NotPattern))
                self.generic_visit(node)

            def visit_AnnAssign(self, node: AnnAssign) -> Any:
                if isinstance(node.target, Name):
                    self.entities.append(
                        TypedEntity(EntityType.Variable, stub_file, tuple(self.scope) + (node.target.id,),
                                    node.lineno, node.end_lineno, ComplexPattern.NotPattern))

        visitor = GetTypedFunVars()
        visitor.visit(stub_tree)
        for e in visitor.entities:
            if len(e.scope) == 1 and arg.value == e.scope[0]:
                return True
        return False

    def is_imported_var(expr) -> bool:
        class GetImported(ScopedVisitor):
            def __init__(self):
                super().__init__()
                self.imported_names = []

            def visit_Import(self, node: Import) -> Any:
                for alias in node.names:
                    self.imported_names.append(alias.name)
                self.generic_visit(node)

            def visit_ImportFrom(self, node: ImportFrom) -> Any:
                for alias in node.names:
                    self.imported_names.append(alias.name)
                self.generic_visit(node)

        visitor = GetImported()
        visitor.visit(src_tree)
        return isinstance(expr, Constant) and expr.value in visitor.imported_names

    res = []
    imported_names = []
    for an_assign in all_assigns:
        if isinstance(an_assign.value, ast.List):
            imported_names = (filter(is_imported_var, list(an_assign.value.elts)))
            if len(list(filter(is_typed_var, imported_names))) != 0:
                res.append(
                    TypedEntity(EntityType.Variable, src_file, ("__all__",), an_assign.lineno, an_assign.end_lineno,
                                ComplexPattern.APIVis))
    return res
