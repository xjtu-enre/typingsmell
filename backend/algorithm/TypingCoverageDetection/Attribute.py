from pathlib import Path

from algorithm.TypingCoverageDetection.CsvItem import CsvItem


class ProjectFunVarAttribute:
    def __init__(self, project_name, funVarCoverage, assignCount):
        self._project_name = project_name
        self._funVarCoverage = funVarCoverage
        self._assignCount = assignCount

    def gen_csv_header(self):
        return "project," \
               "function," \
               "function in stub," \
               "distinct function in stub," \
               "function typed in source," \
               "matched function typed in corresponding stub file," \
               "function typed in corresponding stub file but not matched," \
               "function typed overload in corresponding stub file," \
               "function source file typed rate," \
               "function stub file typed rate," \
               "lvaues," \
               "typed lvaues," \
               "lvaues typed in stub," \
               "name assignment," \
               "subscript assignment," \
               "attribute assignment," \
               "tuple unpacking assignment," \
               "list unpacking assignment," \
               "slice assignment" \
               "\n"

    def gen_csv_item(self):
        return f"{self._project_name}," \
               f"{self._funVarCoverage._fun_num}," \
               f"{self._funVarCoverage._stub_fun_num}," \
               f"{self._funVarCoverage._distinct_stub_fun}," \
               f"{self._funVarCoverage._typed_src_fun_num}," \
               f"{self._funVarCoverage._matched_stub_fun_num}," \
               f"{self._funVarCoverage._stubed_unsourced}," \
               f"{self._funVarCoverage._overload_stub_num}," \
               f"{self._funVarCoverage._typed_src_fun_num / self._funVarCoverage._fun_num}," \
               f"{self._funVarCoverage._matched_stub_fun_num / self._funVarCoverage._fun_num}," \
               f"{self._funVarCoverage._target_num}," \
               f"{self._funVarCoverage._typed_src_target_num}," \
               f"{self._funVarCoverage._matched_typed_stub_target_num}," \
               f"{self._assignCount.name_count}," \
               f"{self._assignCount.subscript_count}," \
               f"{self._assignCount.attribute_count}," \
               f"{self._assignCount.tuple_count}," \
               f"{self._assignCount.list_count}," \
               f"{self._assignCount.slice_count}" \
               "\n"


class FileAttribute(CsvItem):
    def __init__(self, root: Path, file_path: Path, filetype, annotation_num, any_num):
        self._root = root
        self._file_path = file_path
        self._filetype = filetype
        self._any_rate = any_num / annotation_num if annotation_num != 0 else 0
        super().__init__({"file path": str(file_path.relative_to(root)),
                          "file type": filetype,
                          "any rate": self._any_rate})
    def gen_csv_line(self) -> str:
        return "{0},{1},{2}\n".format(self._file_path.relative_to(self._root.parent).__str__().replace("\\", "/"),
                                      self._filetype, self._any_rate)

    @staticmethod
    def gen_csv_header():
        return "file path,file type,any rate\n"
