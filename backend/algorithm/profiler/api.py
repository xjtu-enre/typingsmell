import os
from pathlib import Path
from functools import partial
from collections import defaultdict
from typing import List, Dict
from algorithm.profiler.CsvItem import CsvItem, cat_csv_item

from algorithm.profiler.TypedEntity import TypedEntity, ComplexPattern
from algorithm.profiler.main import iter_dir, init_detectors


class PatternInfo:
    def __init__(self, api_vis: List, extension_typing: List, overload_typing: List, type_compatibility: List,
                 functional_var: List, base_class: List):
        self.ApiVisibility = api_vis
        self.ExtensionTyping = extension_typing
        self.Overload = overload_typing
        self.TypeCompatibility = type_compatibility
        self.FunctionalVariable = functional_var
        self.BaseclassPresentation = base_class


class PatternCount:
    def __init__(self, api_vis: int, extension_typing: int, overload_typing: int, type_compatibility: int,
                 functional_var: int, base_class: int):
        self.ApiVisibility = api_vis
        self.ExtensionTyping = extension_typing
        self.Overload = overload_typing
        self.TypeCompatibility = type_compatibility
        self.FunctionalVariable = functional_var
        self.BaseclassPresentation = base_class


def _from_ent_list(typed_entities: List[TypedEntity], project_path) -> List[Dict]:
    ret = []
    for ent in typed_entities:
        ret.append(ent.toJson(project_path))
    return ret


def get_typing_practice(out_path: str, src: Path, stub: Path = None):
    init_detectors()
    typed_entities = iter_dir(src, stub if stub is not None else src)
    project_path = str(src).replace("\\", '/')
    stub_path = str(stub).replace("\\", '/')
    entities = _from_ent_list(typed_entities, project_path)

    pattern_count = defaultdict(int)
    pattern_info = defaultdict(partial(defaultdict, list))
    if os.path.exists(os.path.join(out_path)) is not True:
        os.makedirs(out_path)
    with open(out_path + "/TypingPatterns.csv", "w") as file:
        for e in typed_entities:
            typed_dic = e.toJson(project_path)
            pattern_count[e.pattern] += 1
            pattern_info[e.pattern][typed_dic['file_path']].append(typed_dic)
            file.write(e.toCsv(project_path) + "\n")

    csv_item = CsvItem({
        "project name": out_path.rsplit('/', 1)[1],
        ComplexPattern.APIVis: pattern_count[ComplexPattern.APIVis],
        ComplexPattern.ExtensionTyping: pattern_count[ComplexPattern.ExtensionTyping],
        ComplexPattern.OverloadTyping: pattern_count[ComplexPattern.OverloadTyping],
        ComplexPattern.TypeCompatibility: pattern_count[ComplexPattern.TypeCompatibility],
        ComplexPattern.FunctionalVar: pattern_count[ComplexPattern.FunctionalVar],
        ComplexPattern.BaseClass: pattern_count[ComplexPattern.BaseClass]
    })

    with open(out_path + "/PatternCount.csv", "w") as file:
        content = cat_csv_item([csv_item])
        file.write(content)
    return PatternCount(pattern_count[ComplexPattern.APIVis],
                        pattern_count[ComplexPattern.ExtensionTyping],
                        pattern_count[ComplexPattern.OverloadTyping],
                        pattern_count[ComplexPattern.TypeCompatibility],
                        pattern_count[ComplexPattern.FunctionalVar],
                        pattern_count[ComplexPattern.BaseClass]), \
           PatternInfo(pattern_info[ComplexPattern.APIVis],
                       pattern_info[ComplexPattern.ExtensionTyping],
                       pattern_info[ComplexPattern.OverloadTyping],
                       pattern_info[ComplexPattern.TypeCompatibility],
                       pattern_info[ComplexPattern.FunctionalVar],
                       pattern_info[ComplexPattern.BaseClass])
