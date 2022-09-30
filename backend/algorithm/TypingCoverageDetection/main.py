import sys
import warnings
from pathlib import Path

from algorithm.TypingCoverageDetection.CsvItem import cat_csv_item, union_csv_items, CsvItem
from algorithm.TypingCoverageDetection.NewClassCounter import ClassCounter
from algorithm.TypingCoverageDetection.filecoveragecalculator import FileCoverageCalculator, ProjeceName
from algorithm.TypingCoverageDetection.funcoveragecalculator import FunCoverageCalculator


def main():
    argv = sys.argv[1:]
    src_dir = Path(argv[0])
    stub_dir = Path(argv[1])
    if len(argv) > 2:
        project_name = argv[2]
    else:
        project_name = src_dir.name

    CovEntry(src_dir, stub_dir, project_name)


def CovEntry(src_dir: Path, stub_dir: Path, project_name: str):
    warnings.warn("CovEntry is deprecated, please use algorithm.pratice.coverage module", DeprecationWarning)
    print(f"\nstart checking project {project_name}")
    project_name_item = ProjeceName(project_name)
    fileCC = FileCoverageCalculator(src_dir, stub_dir)
    fileCC.cal_cov(src_dir, stub_dir)
    fileCC.cal_not_match_stub(src_dir, stub_dir)
    print(fileCC.not_match_lst)
    funCC = FunCoverageCalculator(src_dir, stub_dir)
    funCC.cal_cov(src_dir, stub_dir)
    classC = ClassCounter(src_dir, stub_dir)
    classC.cal_class_use()

    file_CovItem = fileCC.cov_rate()
    fun_CovItem = funCC.cov_rate()
    new_class_Item = classC.new_classes_item()
    assignCategory = funCC.assign_category()
    type_related_line = funCC.type_related_line()
    print(file_CovItem)
    print(fun_CovItem)
    print(assignCategory)
    print(new_class_Item)
    csv_content = union_csv_items(project_name_item, file_CovItem, fun_CovItem, assignCategory, type_related_line,
                                  new_class_Item)
    out_name = project_name + "Attribute.csv"
    with open(out_name, "w") as file:
        file.write(csv_content)

    out_name = project_name + "NotMatchStubs.csv"
    with open(out_name, "w") as file:
        for item in fileCC.not_match_lst:
            file.write(str(item).replace("\\", "/") + "\n")

    out_name = project_name + "NotMatchFunctions.csv"
    with open(out_name, "w") as file:
        for item in funCC.not_match_fun_list:
            file.write(item.replace("\\", "/") + "\n")

    out_name = project_name + "FileType.csv"
    csv_content = cat_csv_item(funCC.get_file_attr())
    with open(out_name, "w") as file:
        file.write(csv_content)

    out_name = project_name + "OverloadCount.csv"
    with open(out_name, "w") as file:
        if len(funCC.overload_dict_matched) != 0:
            min_overload_matched = min(funCC.overload_dict_matched.items(), key=lambda pair: pair[0])[0]
            max_overload_matched = max(funCC.overload_dict_matched.items(), key=lambda pair: pair[0])[0]
        else:
            min_overload_matched = max_overload_matched = 0
        if len(funCC.overload_dict_all) != 0:
            min_overload_all = min(funCC.overload_dict_all.items(), key=lambda pair: pair[0])[0]
            max_overload_all = max(funCC.overload_dict_all.items(), key=lambda pair: pair[0])[0]
        else:
            min_overload_all = max_overload_all = 0
        csvItem = CsvItem({"project": project_name,
                           "functions be overloadded(matched)": funCC.overload_stub_matched_num,
                           "funcitons_overload_2(matched)": funCC.overload_dict_matched[2],
                           "funcitons_overload_3(matched)": funCC.overload_dict_matched[3],
                           "min overload(matched)": min_overload_matched,
                           "max overload(matched)": max_overload_matched,
                           "max overload function(matched)": funCC.max_overload_matched_fun if funCC.max_overload_matched_fun is not None else "",
                           "functions be overloadded(all)": funCC.overload_stub_all_num,
                           "funcitons_overload_2(all)": funCC.overload_dict_all[2],
                           "funcitons_overload_3(all)": funCC.overload_dict_all[3],
                           "min overload(all)": min_overload_all,
                           "max overload(all)": max_overload_all,
                           "max overload function(all)": funCC.max_overload_all_fun if funCC.max_overload_all_fun is not None else ""})
        csv_content = cat_csv_item([csvItem])
        file.write(csv_content)
    print(f"project {project_name} checked")

    classC.dump_new_class(project_name)
    classC.dump_sub_class_rel(project_name)

    with open(project_name + "TypeRelatedLines.csv", "w", encoding="utf-8") as file:
        file.write("TypeRelatedLines")
        for item in funCC.type_related_lines:
            file.write(item + "\n")


if __name__ == '__main__':
    main()
