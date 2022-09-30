from pathlib import Path

from CExtension import get_extension_typing
from algorithm.profiler.OverloadDetector import get_overload_functionDef
from algorithm.profiler.TypeCompatibility import get_version_comp_pattern_usage

if __name__ == '__main__':
    file_path = "../test/function_base.pyi"
    entity_list = get_version_comp_pattern_usage(Path(file_path))
    for entity in entity_list:
        print(entity)

    entity_list = get_overload_functionDef(Path(file_path))
    for entity in entity_list:
        print(entity)

    src_path = "D:\\WorkSpace\\Data-Set\\numpy\\numpy"
    stub_path = "D:\\WorkSpace\\Data-Set\\numpy\\numpy"
    entity_list = get_extension_typing(Path(src_path), Path(stub_path))
    for entity in entity_list:
        print(entity)