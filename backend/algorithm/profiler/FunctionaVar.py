import ast
from ast import Assign, FunctionDef
from pathlib import Path
from typing import List

from algorithm.profiler.ScopedVisitor import ScopedVisitor
from algorithm.profiler.TypedEntity import TypedEntity, EntityType, ComplexPattern


def get_var_entities(src_path: Path) -> List[TypedEntity]:
    class GetVarVisitor(ScopedVisitor):
        def __init__(self):
            super().__init__()
            self.var_entities: List[TypedEntity] = []

        def visit_Assign(self, node: Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.var_entities.append(
                        TypedEntity(EntityType.Variable, src_path, tuple(self.scope + [target.id]), node.lineno,
                                    node.end_lineno, ComplexPattern.FunctionalVar)
                    )
            self.generic_visit(node)

    visitor = GetVarVisitor()
    with open(src_path, "r", encoding="utf-8") as file:
        visitor.visit(ast.parse(file.read()))
    return visitor.var_entities


def get_fun_entities(src_path: Path) -> List[TypedEntity]:
    class GetFunVisitor(ScopedVisitor):
        def __init__(self):
            super().__init__()
            self.fun_entities: List[TypedEntity] = []

        def visit_FunctionDef(self, node: FunctionDef):
            self.fun_entities.append(
                TypedEntity(EntityType.Variable, src_path, tuple(self.scope), node.lineno, node.end_lineno,
                            ComplexPattern.FunctionalVar))
            self.generic_visit(node)

    visitor = GetFunVisitor()
    with open(src_path, "r") as file:
        visitor.visit(ast.parse(file.read()))
    return visitor.fun_entities


def get_functional_assign(src_path: Path, stub_path: Path):
    var_entities = get_var_entities(src_path)
    fun_entities = get_fun_entities(stub_path)

    def is_functional_assign(var: TypedEntity) -> bool:
        for fun in fun_entities:
            if var.scope == fun.scope:
                return True
        return False

    functional_vars = filter(is_functional_assign, var_entities)
    return functional_vars
