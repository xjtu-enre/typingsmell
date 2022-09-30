import os
import sys
import warnings
from collections import defaultdict
from pathlib import Path
from typing import List, Callable, Optional

from algorithm.profiler.CsvItem import CsvItem, cat_csv_item
from algorithm.profiler.ApiVisibility import get_api_visibility
from algorithm.profiler.BasePresentation import get_base_presentation
from algorithm.profiler.CExtension import get_extension_typing
from algorithm.profiler.FunctionaVar import get_functional_assign
from algorithm.profiler.OverloadDetector import get_overload_functionDef
from algorithm.profiler.TypeCompatibility import get_version_comp_pattern_usage
from algorithm.profiler.TypedEntity import TypedEntity, ComplexPattern
from algorithm.profiler.getattrUsageDetector import get_getattr_usage
from algorithm.profiler.Util import find

SrcDetector = Callable[[Path], List[TypedEntity]]
PairDetector = Callable[[Path, Path], List[TypedEntity]]
ProjectDetector = Callable[[Path, Path], List[TypedEntity]]
StubDetector = Callable[[Path], List[TypedEntity]]

src_detectors: List[Callable[[Path], List[TypedEntity]]] = []
pair_detectors: List[Callable[[Path, Path], List[TypedEntity]]] = []
project_detectors: List[Callable[[Path, Path], List[TypedEntity]]] = []
stub_detectors: List[Callable[[Path], List[TypedEntity]]] = []


def get_overload(typed_entities: List[TypedEntity]) -> int:
    scope_set = set()
    for e in typed_entities:
        scope_set.add((str(e.file),) + e.scope)
    return len(scope_set)


def main():
    warnings.warn("Deprecated", DeprecationWarning)
    src_dir = Path(sys.argv[1])
    stub_dir = Path(sys.argv[2])
    print(src_dir)
    print(stub_dir)
    if not src_dir.exists() or not src_dir.is_dir():
        return
    if (len(sys.argv) > 3) and sys.argv[3] == "-o":
        out_name = sys.argv[4]
    else:
        out_name = src_dir.name
    init_detectors()
    typed_entities = detect_entry(src_dir, stub_dir)
    pattern_count = defaultdict(int)
    with open(out_name + "TypingPatterns.csv", "w") as file:
        for e in typed_entities:
            pattern_count[e.pattern] += 1
            file.write(str(e) + "\n")
    pattern_count[ComplexPattern.OverloadTyping] = get_overload(typed_entities)
    csv_item = CsvItem({
        "project name": out_name,
        ComplexPattern.APIVis: pattern_count[ComplexPattern.APIVis],
        ComplexPattern.BaseClass: pattern_count[ComplexPattern.BaseClass],
        ComplexPattern.ExtensionTyping: pattern_count[ComplexPattern.ExtensionTyping],
        ComplexPattern.OverloadTyping: pattern_count[ComplexPattern.OverloadTyping],
        ComplexPattern.TypeCompatibility: pattern_count[ComplexPattern.TypeCompatibility],
        ComplexPattern.FunctionalVar: pattern_count[ComplexPattern.FunctionalVar]
    })

    with open(out_name + "PatternCount.csv", "w") as file:
        content = cat_csv_item([csv_item])
        file.write(content)

    return 0


def init_detectors():
    global project_detectors, src_detectors, pair_detectors, stub_detectors

    project_detectors = []
    src_detectors =[]
    pair_detectors = []
    stub_detectors = []
    project_detectors.append(get_extension_typing)
    src_detectors += [get_version_comp_pattern_usage, get_overload_functionDef, get_getattr_usage]
    pair_detectors += [get_base_presentation, get_functional_assign, get_api_visibility]
    stub_detectors += [get_overload_functionDef]


def detect_entry(src_dir: Path, stub_dir: Optional[Path] = None):
    complex_typed_entities = []
    complex_typed_entities += project_level_detect(src_dir, stub_dir)
    entities = iter_dir(src_dir, stub_dir)
    return entities + complex_typed_entities


def project_level_detect(src_dir: Path, stub_dir: Path) -> List[TypedEntity]:
    res = []
    for detector in project_detectors:
        res += detector(src_dir, stub_dir)
    return res


def file_level_detect(file: Path) -> List[TypedEntity]:
    res = []
    for detector in src_detectors:
        res += detector(file)
    return res


def stub_level_detect(file: Path) -> List[TypedEntity]:
    res = []
    for detector in stub_detectors:
        res += detector(file)
    return res


def pair_level_detect(src_path: Path, stub_path: Path) -> List[TypedEntity]:
    res = []
    for detector in pair_detectors:
        res += detector(src_path, stub_path)
    return res


def iter_dir(src_dir: Path, stub_dir: Path) -> List[TypedEntity]:
    res = []
    with os.scandir(src_dir) as entries:
        for entry in entries:
            if entry.is_dir():
                stub_dir_path = find(entry.name, stub_dir)
                if stub_dir_path is not None:
                    res += iter_dir(Path(entry), stub_dir_path)
                else:
                    res += iter_dir(Path(entry), Path(entry))
            elif entry.name.endswith(".py"):
                res += file_level_detect(Path(entry))
                stub_file = find(entry.name[:-3] + ".pyi", stub_dir)
                if stub_file is not None:
                    res += file_level_detect(stub_file)
                    res += stub_level_detect(stub_file)
                    res += pair_level_detect(Path(entry), stub_file)
            elif entry.name.endswith(".pyi") and find(entry.name[:-4] + ".py", src_dir) is None:
                res += file_level_detect(Path(entry))

    return res
