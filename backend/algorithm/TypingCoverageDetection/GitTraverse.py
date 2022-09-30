import ast
import os
import sys
import warnings
from ast import NodeVisitor, AnnAssign, FunctionDef, AST
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from git import Repo, GitCommandError

from algorithm.TypingCoverageDetection.CsvItem import CsvItem, cat_csv_item


class HasTypingSingle(NodeVisitor):
    def __init__(self):
        self.typed = False

    def is_typed(self, tree: AST) -> bool:
        self.visit(tree)
        return self.typed

    def visit_AnnAssign(self, node: AnnAssign):
        self.typed = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionDef):

        def is_typed_arg(an_arg) -> bool:
            if an_arg.annotation is not None:
                return True
            if an_arg.type_comment is not None:
                return True
            return False

        for an_arg in node.args.args:
            if is_typed_arg(an_arg):
                self.typed = True
        for an_arg in node.args.kwonlyargs:
            if is_typed_arg(an_arg):
                self.typed = True

        for an_arg in node.args.posonlyargs:
            if is_typed_arg(an_arg):
                self.typed = True

        if node.args.kwarg is not None:
            an_arg = node.args.kwarg
            if is_typed_arg(an_arg):
                self.typed = True

        if node.args.vararg is not None:
            an_arg = node.args.vararg
            if is_typed_arg(an_arg):
                self.typed = True

        if node.returns is not None:
            self.typed = True
        self.generic_visit(node)


class HasInlineTyping:
    def __init__(self, core_dir: Path):
        self.core_dir = core_dir

    def isInlinedTyped(self, src_dir: Path = None) -> bool:
        if src_dir is None:
            src_dir = self.core_dir

        with os.scandir(src_dir) as entries:
            for entry in entries:
                if entry.is_dir():
                    if self.isInlinedTyped(Path(entry)) == True:
                        return True
                elif entry.name.endswith(".py"):
                    try:
                        with open(entry, "r", encoding="utf-8") as file:
                            try:
                                tree = ast.parse(file.read())
                                if HasTypingSingle().is_typed(tree):
                                    return True
                            except SyntaxError:
                                pass
                    except UnicodeDecodeError:
                        pass
            return False


def same_month(lhs: datetime, rhs: datetime) -> bool:
    return lhs.year == rhs.year and lhs.month == rhs.month


def find_start_typing_release(repo: Repo, core_dir: Path) -> Tuple[
    Optional[datetime], Optional[datetime], Optional[datetime], Optional[datetime]]:
    warnings.warn("Deprecated", DeprecationWarning)
    tags = repo.tags
    has_inline_typed = []
    released = []

    for tag in tags:
        if "." in tag.name:
            print(tag)
            try:
                repo.git.checkout(tag)
            except Exception:
                continue
            commit = repo.commit(tag)
            commit_date: datetime = commit.committed_datetime
            if len(released) != 0 and same_month(released[-1], commit_date):
                continue
            released.append(commit_date)
            typedChecker = HasInlineTyping(core_dir)
            if typedChecker.isInlinedTyped():
                has_inline_typed.append(commit_date)
    has_inline_typed.sort()
    released.sort()
    if len(released) == 0:
        released_res: Tuple[Optional[datetime],Optional[datetime]] = None, None
    else:
        released_res = released[0], released[-1]

    if len(has_inline_typed) != 0:
        inlined_res: Tuple[Optional[datetime],Optional[datetime]] = has_inline_typed[0], has_inline_typed[-1]
    else:
        inlined_res = None, None
    return released_res + inlined_res


def find_start_stub(repo: Repo, core_dir: Path):
    warnings.warn("Deprecated", DeprecationWarning)
    tags = repo.tags
    has_stub_date = []
    commit_dates = []
    for tag in tags:
        if "." in tag.name:
            print(tag)
            try:
                repo.git.checkout(tag)
            except:
                continue
            commit = repo.commit(tag)
            commit_date: datetime = commit.committed_datetime
            if len(commit_dates) != 0 and same_month(commit_dates[-1], commit_date):
                continue
            commit_dates.append(commit_date)
            if len(has_stub_date) != 0 and same_month(has_stub_date[-1], commit_date):
                continue
            for root, dirs, files in os.walk(core_dir):
                for file in files:
                    if file.endswith(".pyi"):
                        has_stub_date.append(commit_date)
    has_stub_date.sort()
    print(len(has_stub_date))
    return (has_stub_date[0], has_stub_date[-1]) if len(has_stub_date) != 0 else None


def find_start_inline_typing_all(repo: Repo, core_dir: Path) -> Tuple[
    datetime, datetime, Optional[datetime], Optional[datetime]]:
    warnings.warn("Deprecated", DeprecationWarning)
    default_branch = repo.git.__getattr__("symbolic-ref")("refs/remotes/origin/HEAD").split("/")[-1]
    repo.git.checkout(default_branch)

    commits = repo.iter_commits()
    commits = sorted(commits, key=lambda commit: commit.committed_datetime)
    has_inline_typed = []
    commit_dates: List[datetime] = []
    for commit in commits:
        commit_date = commit.committed_datetime
        if len(commit_dates) != 0 and same_month(commit_dates[-1], commit_date):
            continue
        print(commit_date)
        try:
            repo.git.checkout(commit)
        except Exception:
            continue
        commit_dates.append(commit_date)

        typedChecker = HasInlineTyping(core_dir)
        if typedChecker.isInlinedTyped():
            has_inline_typed.append(commit_date)
    has_inline_typed.sort()
    commit_dates.sort()

    if len(has_inline_typed) != 0:
        return commit_dates[0], commit_dates[-1], has_inline_typed[0], has_inline_typed[-1]
    else:
        return commit_dates[0], commit_dates[-1], None, None


def find_start_stub_typing_all(repo: Repo, core_dir: Path) -> Tuple[Optional[datetime], Optional[datetime]]:
    warnings.warn("Deprecated", DeprecationWarning)
    commits = repo.iter_commits()
    has_stub_date = []
    commit_dates = []
    default_branch = repo.git.__getattr__("symbolic-ref")("refs/remotes/origin/HEAD").split("/")[-1]
    try:
        repo.git.checkout(default_branch)
    except GitCommandError:
        exit(-1)
    for commit in commits:
        commit_date = commit.committed_datetime
        if len(commit_dates) != 0 and same_month(commit_dates[-1], commit_date):
            continue
        try:
            repo.git.checkout(commit)
        except Exception:
            continue
        commit_dates.append(commit_date)
        for root, dirs, files in os.walk(core_dir):
            for file in files:
                if file.endswith(".pyi"):
                    has_stub_date.append(commit_date)

    has_stub_date.sort()
    return (has_stub_date[0], has_stub_date[-1]) if len(has_stub_date) != 0 else (None, None)


def align_month(date: datetime) -> str:
    if date is None:
        return "None"
    else:
        return f"{date.year}-{date.month}-{date.day}"


def start_typing_workflow():
    warnings.warn("deprecated", DeprecationWarning)
    argv = sys.argv[1:]
    src_dir = Path(argv[0])
    src_core = Path(argv[0])
    stub_dir = Path(argv[2])
    stub_core = Path(argv[2])
    if len(argv) > 4:
        project_name = argv[4]
    else:
        project_name = src_dir.name

    print(f"start find first typing practice of {project_name}")
    out_name = project_name + "TypingDate.csv"
    if Path(out_name).exists():
        print("outfile exists, find typing process passed")
        return

    stubRepo = Repo(stub_dir)
    srcRepo = Repo(src_dir)

    first_commit_date, current_commit, first_inline_typed_date, current_inline_typed_date = find_start_inline_typing_all(
        srcRepo, src_core)
    first_stub_date, current_stub_date = find_start_stub_typing_all(stubRepo, stub_core)

    def optional_min(x: Optional[datetime], y: Optional[datetime]):
        warnings.warn("Deprecated", DeprecationWarning)
        if x is None:
            return y
        if y is None:
            return x
        return min(x, y)

    start_typing_date = optional_min(first_inline_typed_date, first_stub_date)
    current_typing_date = optional_min(current_inline_typed_date, current_stub_date)

    start_stub_res = find_start_stub(stubRepo, stub_core)
    start_inline_typing_res = find_start_typing_release(srcRepo, src_core)
    if start_stub_res is None:
        start_stub_date = current_stub_date_release = None
    else:
        start_stub_date, current_stub_date_release = start_stub_res

    if len(start_inline_typing_res) == 4:
        start_typing_date_release = align_month(
            start_inline_typing_res[2] if start_stub_date is None or start_inline_typing_res[
                2] < start_stub_date else start_stub_date)
    else:
        start_typing_date_release = align_month(start_stub_date)

    if len(start_inline_typing_res) == 4:
        current_typing_date_release = align_month(
            start_inline_typing_res[3] if current_stub_date_release is None or start_inline_typing_res[
                3] < current_stub_date_release else current_stub_date_release)
    else:
        current_typing_date_release = align_month(current_stub_date_release)

    csv_item = CsvItem({"project name": str(project_name),
                        "first released date": align_month(start_inline_typing_res[0]),
                        "current released date": align_month(start_inline_typing_res[1]),
                        "start typing release date": start_typing_date_release,
                        "current typing release date": current_typing_date_release,
                        "fist commit date": align_month(first_commit_date),
                        "current commit date": align_month(current_commit),
                        "start typing date": align_month(start_typing_date),
                        "current typing date": align_month(current_typing_date)})

    out_name = project_name + "TypingDate.csv"
    with open(out_name, "w", encoding="utf-8") as file:
        csv_content = cat_csv_item([csv_item])
        print(csv_content)
        file.write(csv_content)


if __name__ == '__main__':
    start_typing_workflow()
