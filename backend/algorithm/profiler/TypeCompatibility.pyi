from pathlib import Path
from typing import overload, List
from ast import Import, ImportFrom

from algorithm.profiler.TypedEntity import TypedEntity


@overload
def is_importing_class(node: Import, file_path) -> bool:
    ...

@overload
def is_importing_class(node: ImportFrom, file_path) -> bool:
    ...

def get_version_comp_pattern_usage(file_path: Path) -> List[TypedEntity]:
    ...