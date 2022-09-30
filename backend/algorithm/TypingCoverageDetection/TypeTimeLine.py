import sys
import warnings
from pathlib import Path
from typing import List, Dict

from git import Repo, GitCommandError

from algorithm.TypingCoverageDetection.GitTraverse import same_month
from algorithm.TypingCoverageDetection.CsvItem import CsvItem
from algorithm.TypingCoverageDetection.filecoveragecalculator import FileCoverageCalculator
from algorithm.TypingCoverageDetection.funcoveragecalculator import FunCoverageCalculator
from algorithm.profiler.CsvItem import union_csv_items_1
from app.utils import FormatTime
from app.utils import DealFile


def draw_timeline(repo: Repo, project_encodename) -> (List[CsvItem], List[Dict]):
    default_branch = repo.git.__getattr__("symbolic-ref")("refs/remotes/origin/HEAD").split("/")[-1]
    DealFile().repo_repair(project_encodename, default_branch)
    # try:
    #     repo.git.checkout(default_branch)
    # except GitCommandError:
    #     exit(-1)
    commits = repo.iter_commits()
    commit_dates = []
    cov_infos = []
    commit_cov = []
    for commit in commits:
        commit_date = commit.committed_datetime
        if len(commit_dates) != 0 and same_month(commit_dates[-1], commit_date):
            continue
        # if commit_date.year <= 2020:
        #     return commit_cov, cov_infos
        try:
            # repo.git.checkout(commit)
            DealFile().repo_repair(project_encodename, default_branch)
        except Exception:
            continue
        commit_dates.append(commit_date)
        print(f"computing the commit at {commit_date}")
        root_path = Path(repo.working_dir)
        funCC = FunCoverageCalculator(root_path, root_path)
        funCC.cal_cov()
        fileCC = FileCoverageCalculator(root_path, root_path)
        fileCC.cal_cov(root_path, root_path)

        fileCov = fileCC.cov_rate()
        funCov = funCC.cov_rate()
        typed_function_num = funCov["typed function"]
        function_num = funCov["function"]
        type_related_line = funCC.type_related_line()
        type_related_line_num = type_related_line["type related line in source"] + fileCov["matched stub file line"]
        line_num = fileCov["source file line"] + fileCov["matched stub file line"]
        typed_file_num = funCov["typed file"]
        file_num = fileCov["source file"]
        var_num = funCov["var num"]
        typed_var_num = funCov["typed var num"]
        var_cov = typed_var_num / var_num if var_num != 0 else 0
        file_cov = typed_file_num / file_num if file_num != 0 else 0
        line_cov = type_related_line_num / line_num if line_num != 0 else 0
        fun_cov = typed_function_num / function_num if function_num != 0 else 0
        any_rate = funCC.any_num / funCC.annotation_num if funCC.annotation_num != 0 else 0
        funCov = union_csv_items_1(CsvItem({"date": FormatTime().format_time(commit_date),
                                            "commit ID": str(commit),
                                            "Coverage(file)": file_cov,
                                            "Coverage(func)": fun_cov,
                                            "Coverage(loc)": line_cov,
                                            "Coverage(var)": var_cov,
                                            "type manner": "&".join(funCC.type_manner),
                                            "Any rate": any_rate}),
                                   funCov, fileCov)
        cov_infos.append(funCov)
        commit_cov.append({"date": FormatTime().format_time(commit_date),
                           # "commit ID": str(commit),
                           "file": file_cov,
                           "func": fun_cov,
                           "loc": line_cov,
                           "var": var_cov})
    return commit_cov, cov_infos


def draw_timeline_workflow():
    warnings.warn('deprecated!',DeprecationWarning)
    argv = sys.argv[1:]
    src_dir = Path(argv[0])
    project_name = src_dir.name
    out_name = project_name + "TypingTimeline.csv"
    if Path(out_name).exists():
        print("outfile exists, draw timeline process passed")
        return
    src_repo = Repo(src_dir)
    _, timeline = draw_timeline(src_repo, '')
    with open(out_name, "w") as file:
        file.write(timeline[0].gen_csv_header())
        for item in reversed(timeline):
            file.write(item.gen_csv_line())


if __name__ == '__main__':
    draw_timeline_workflow()
