import os
import pathlib
from pathlib import Path

from algorithm.TypingCoverageDetection.CsvItem import CsvItem
from algorithm.TypingCoverageDetection.Util import find


class ProjeceName(CsvItem):
    def __init__(self, name):
        self.project_name = name

    def __str__(self) -> str:
        return self.project_name

    @staticmethod
    def gen_csv_header() -> str:
        return f"project name\n"

    def gen_csv_line(self) -> str:
        return f"{self.project_name}\n"


class FileCoverdage(CsvItem):
    def __init__(self, file_num, stub_num, file_line_num, stub_line_num, not_empty_file):
        self._file_num = file_num
        self._stub_num = stub_num
        self._file_line_num = file_line_num
        self._stub_line_num = stub_line_num
        self._not_empty_file_num = not_empty_file

    def __str__(self) -> str:
        return (f"source file: {self._file_num}\n"
                f"not empty source: {self._not_empty_file_num}\n"
                f"matched stub file: {self._stub_num}\n"
                f"stub coverage: {self._stub_num / self._file_num}\n"
                f"source file line: {self._file_line_num}\n"
                f"stub file line: {self._stub_line_num}\n"
                f"stub line rate: {self._stub_line_num / (self._file_line_num + self._stub_line_num)}")

    @staticmethod
    def gen_csv_header() -> str:
        return "source file,matched stub file,stub coverage,source file line,stub file line,stub line rate\n"

    def gen_csv_line(self) -> str:
        return f"{self._file_num},{self._stub_num},{self._stub_num / self._file_num},{self._file_line_num}," \
               f"{self._stub_line_num},{self._stub_line_num / (self._file_line_num + self._stub_line_num)}\n"


class FileCoverageCalculator:
    def __init__(self, src_root: Path, stub_root: Path):
        self._src_line_num = 0
        self._matched_stub_line_num = 0
        self._file_num = 0
        self._matched_stub_num = 0
        self._non_empty_file_num = 0
        self.not_match_lst = []
        self.src_root = src_root.parent
        self.stub_root = stub_root.parent

    def cov_rate(self):
        return CsvItem({"source file": self._file_num, "matched stub file": self._matched_stub_num,
                        "source file line": self._src_line_num, "matched stub file line": self._matched_stub_line_num,
                        "not empty source": self._non_empty_file_num, "unmatched stub file": len(self.not_match_lst)})

    def cal_cov(self, src: pathlib.Path, stub: Path):
        with os.scandir(src) as entries:
            for entry in entries:
                if entry.is_dir():
                    stub_dir_path = find(entry.name, stub)
                    if stub_dir_path is None:
                        self.file_count(entry)
                    else:
                        self.cal_cov(entry, stub_dir_path)
                elif entry.name.endswith(".py"):
                    self.file_count(entry)
                    stub_file = find(entry.name[:-3] + ".pyi", stub)
                    if stub_file is not None:
                        self._matched_stub_num += 1
                        with open(stub_file, "r", encoding="utf-8") as file:
                            lines = file.read().split('\n')
                            for line in lines:
                                tokens = line.split()
                                if tokens:
                                    if tokens[0][0] != '#':
                                        self._matched_stub_line_num += 1

    def cal_not_match_stub(self, src: Path, stub: Path):
        with os.scandir(stub) as entries:
            for entry in entries:
                if entry.is_dir():
                    src_dir_path = find(entry.name, src)
                    if src_dir_path is None:
                        self.file_count(entry)
                    else:
                        self.cal_not_match_stub(src_dir_path, entry)
                elif entry.name.endswith(".pyi"):
                    src_file = find(entry.name[:-4] + ".py", src)
                    if src_file is None:
                        self.not_match_lst.append(Path(entry).relative_to(self.stub_root))

    def file_count(self, path: Path) -> None:
        if path.is_file() and path.name.endswith(".py"):
            self._file_num += 1
            not_empty = False
            with open(path, "r", encoding="utf-8") as file:
                try:
                    lines = file.read().split('\n')
                except UnicodeDecodeError:
                    return
                for line in lines:
                    tokens = line.split()
                    if tokens:
                        if tokens[0][0] != '#':
                            not_empty = True
                            self._src_line_num += 1
            if not_empty:
                self._non_empty_file_num += 1
        elif path.is_dir():
            with os.scandir(path) as entries:
                for entry in entries:
                    self.file_count(entry)
