import ast
from pathlib import Path
from typing import List

from algorithm.profiler.TypedEntity import TypedEntity, EntityType, ComplexPattern


def get_getattr_usage(file_path: Path) -> List[TypedEntity]:
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read())
        except:
            return []
        res = []
        for stmt in tree.body:
            if isinstance(stmt, ast.FunctionDef):
                if stmt.name == "__getattr__":
                    res.append(
                        TypedEntity(EntityType.Function, file_path, ("__getattr__",), stmt.lineno, stmt.end_lineno,
                                    ComplexPattern.GetAttrDef))
        return res
