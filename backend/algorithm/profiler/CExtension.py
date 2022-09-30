import os
from pathlib import Path
from typing import List

from algorithm.profiler.TypedEntity import TypedEntity, EntityType, ComplexPattern
from algorithm.profiler.Util import find


def get_extension_typing(src_dir: Path, stub_dir: Path) -> List[TypedEntity]:
    res: List[TypedEntity] = []
    for entry in os.scandir(src_dir):
        if entry.name.endswith(".pyx") or entry.name.endswith(".pyc") or entry.name.endswith(".pxd"):
            stub_name = entry.name[:-3] + "pyi"
            mypy_stub_name = entry.name[:-3] + "pxi"
            stub_file = find(stub_name, stub_dir)
            mypy_stub_file = find(mypy_stub_name, stub_dir)
            if stub_file is not None:
                res += [TypedEntity(EntityType.StubFile, stub_file, tuple(), 0, 0,ComplexPattern.ExtensionTyping)]
            if mypy_stub_file is not None:
                res += [TypedEntity(EntityType.StubFile, mypy_stub_file, tuple(), 0, 0,ComplexPattern.ExtensionTyping)]
        elif Path(entry).is_dir():
            sub_stub = find(entry.name, stub_dir)
            if sub_stub is not None:
                res += get_extension_typing(Path(entry), sub_stub)
            else:
                res += get_extension_typing(Path(entry), Path(entry))
    return res
