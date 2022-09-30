import ast
from ast import FunctionDef
from collections import defaultdict
from pathlib import Path
from typing import List, Any

from algorithm.profiler.ScopedVisitor import ScopedVisitor
from algorithm.profiler.TypedEntity import TypedEntity, EntityType, ComplexPattern


class FunctionProfiler(ScopedVisitor):
    def __init__(self, file_path: Path):
        super().__init__()
        self.functions: List[TypedEntity] = []
        self.file_path: Path = file_path

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        self.functions.append(
            TypedEntity(EntityType.Function, self.file_path, tuple(self.scope), node.lineno, node.end_lineno,
                        ComplexPattern.OverloadTyping))
        self.generic_visit(node)


def get_overload_functionDef(file_path: Path) -> List[TypedEntity]:
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read())
        except:
            return []
        funProfiler = FunctionProfiler(file_path)
        funProfiler.visit(tree)
        functions = funProfiler.functions
        overload_counter = defaultdict(int)
        for function in functions:
            overload_counter[function.scope] += 1

        res = []
        for function in functions:
            if overload_counter[function.scope] > 1:
                res.append(function)
        return res
