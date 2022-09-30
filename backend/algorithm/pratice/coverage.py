from __future__ import division
import os
import csv
from pathlib import Path
from git import Repo
from algorithm.TypingCoverageDetection.CsvItem import cat_csv_item, union_csv_items, CsvItem
from algorithm.TypingCoverageDetection.NewClassCounter import ClassCounter
from algorithm.TypingCoverageDetection.filecoveragecalculator import FileCoverageCalculator, ProjeceName
from algorithm.TypingCoverageDetection.funcoveragecalculator import FunCoverageCalculator
from algorithm.TypingCoverageDetection.TypeTimeLine import draw_timeline
from app.models.errors import ConcurrencyError
from app.utils import DealFile

class CoverageData:
    def __init__(self, file, func, loc, var):
        self.file = file
        self.fun = func
        self.loc = loc
        self.var = var


class Coverage:
    project_path = './assets/projects/'
    output_path = "./assets/calculation/"

    @classmethod
    def get_coverage(cls, project_name: str, stub: str):
        print(f"\nstart checking project {project_name} coverage")
        src_dir = Path(cls.project_path + project_name)
        stub_dir = Path(cls.project_path + stub)
        project_name_item = ProjeceName(project_name)
        fileCC = FileCoverageCalculator(src_dir, stub_dir)
        fileCC.cal_cov(src_dir, stub_dir)
        fileCC.cal_not_match_stub(src_dir, stub_dir)
        funCC = FunCoverageCalculator(src_dir, stub_dir)
        funCC.cal_cov(src_dir, stub_dir)
        classC = ClassCounter(src_dir, stub_dir)
        classC.cal_class_use()

        file_CovItem = fileCC.cov_rate()
        fun_CovItem = funCC.cov_rate()
        new_class_Item = classC.new_classes_item()
        assignCategory = funCC.assign_category()

        typed_function_num = fun_CovItem["typed function"]
        function_num = fun_CovItem["function"]
        type_related_line = funCC.type_related_line()
        type_related_line_num = type_related_line["type related line in source"] + file_CovItem[
            "matched stub file line"]
        line_num = file_CovItem["source file line"] + file_CovItem["matched stub file line"]
        typed_file_num = fun_CovItem["typed file"]
        file_num = file_CovItem["source file"]
        var_num = fun_CovItem["var num"]
        typed_var_num = fun_CovItem["typed var num"]
        var_cov = typed_var_num / var_num if var_num != 0 else 0
        file_cov = typed_file_num / file_num if file_num != 0 else 0
        loc_cov = type_related_line_num / line_num if line_num != 0 else 0
        fun_cov = typed_function_num / function_num if function_num != 0 else 0

        csv_content = union_csv_items(project_name_item, file_CovItem, fun_CovItem, assignCategory, type_related_line,
                                      new_class_Item)
        coverage_out_dir = cls.output_path + project_name
        if os.path.exists(coverage_out_dir) is not True:
            os.makedirs(coverage_out_dir)

        with open(coverage_out_dir + "/Attribute.csv", "w") as file:
            file.write(csv_content)

        with open(coverage_out_dir + "/NotMatchStubs.csv", "w") as file:
            for item in fileCC.not_match_lst:
                file.write(str(item).replace("\\", "/") + "\n")

        with open(coverage_out_dir + "/NotMatchFunctions.csv", "w") as file:
            for item in funCC.not_match_fun_list:
                file.write(item.replace("\\", "/") + "\n")

        csv_content = cat_csv_item(funCC.get_file_attr())
        with open(coverage_out_dir + "/FileType.csv", "w") as file:
            file.write(csv_content)

        with open(coverage_out_dir + "/OverloadCount.csv", "w") as file:
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

        classC.dump_new_class(project_name, Coverage.output_path)
        classC.dump_sub_class_rel(project_name, Coverage.output_path)

        with open(coverage_out_dir + "/TypeRelatedLines.csv", "w", encoding="utf-8") as file:
            file.write("TypeRelatedLines")
            for item in funCC.type_related_lines:
                file.write(item + "\n")

        return CoverageData(file_cov, fun_cov, loc_cov, var_cov), file_num, line_num, "&".join(funCC.type_manner)

    @classmethod
    def get_commit_coverage(cls, project_name):
        commit_coverage_out = cls.output_path + project_name + '/TypingTimeline.csv'
        if Path(commit_coverage_out).exists():
            commit_cov = []
            with open(commit_coverage_out, "r") as f:
                next(f)
                for line in csv.reader(f):
                    commit_cov.append(
                        {'date': line[0], 'file': line[2], 'func': line[3], 'loc': line[4], 'var': line[5]})
            return commit_cov
        elif DealFile().get_cal_steps(project_name) == 1 and DealFile().get_running(project_name):
            raise ConcurrencyError("该项目正在进行历史Commit分析!")
        else:
            # DealFile().copy_repo(project_name)
            # temp_dir = Path(cls.project_path + "Temp/" + project_name)
            # temp_repo = Repo(temp_dir)
            repo = Repo(Path(cls.project_path + project_name))
            ver = repo.commit().hexsha
            commit_cov, timeline = draw_timeline(repo, project_name)
            print("All commits computed!")
            out_file = cls.output_path + project_name
            if Path(out_file).exists() is False:
                os.makedirs(out_file)
            with open(commit_coverage_out, "w") as file:
                file.write(timeline[0].gen_csv_header())
                for item in reversed(timeline):
                    file.write(item.gen_csv_line())
            commit_cov.reverse()
            DealFile().repo_repair(project_name, ver)
            repo.close()
            return commit_cov
