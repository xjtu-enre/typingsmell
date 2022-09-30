import ast
import os
import pathlib
from ast import NodeVisitor, FunctionDef, ClassDef, Assign, Name, AnnAssign, Import, ImportFrom
from collections import defaultdict
from pathlib import Path
from typing import Any, List, Tuple, Set

import asttokens

from algorithm.TypingCoverageDetection.Attribute import FileAttribute
from algorithm.TypingCoverageDetection.CsvItem import CsvItem
from algorithm.TypingCoverageDetection.Util import find


class FunVarCoverage(CsvItem):
    def __init__(self, fun_num, stub_fun_num, matched_stub_fun_num, typed_src_fun_num, var_num, typed_var_num,
                 matched_stub_var_num, distinct_stub_fun, stubed_unsourced, overload_stub_num):
        self._fun_num = fun_num
        self._stub_fun_num = stub_fun_num
        self._matched_stub_fun_num = matched_stub_fun_num
        self._typed_src_fun_num = typed_src_fun_num
        self._var_num = var_num
        self._typed_var_num = typed_var_num
        self._matched_stub_var_num = matched_stub_var_num
        self._distinct_stub_fun = distinct_stub_fun
        self._stubed_unsourced = stubed_unsourced
        self._overload_stub_num = overload_stub_num

    def __str__(self) -> str:
        return \
            (f"function: {self._fun_num}\n"
             f"function in stub: {self._stub_fun_num}\n"
             f"distinct function in stub: {self._distinct_stub_fun}\n"
             f"function typed in source: {self._typed_src_fun_num}\n"
             f"matched function typed in corresponding stub file: {self._matched_stub_fun_num}\n"
             f"function typed in corresponding stub file but not matched: {self._stubed_unsourced}\n"
             f"function typed overload in corresponding stub file: {self._overload_stub_num}\n"
             f"function source file typed rate: {self._typed_src_fun_num / self._fun_num}\n"
             f"function stub file typed rate: {self._matched_stub_fun_num / self._fun_num}\n"
             f"lvaues: {self._var_num}\n"
             f"typed lvaues in source: {self._typed_var_num}\n"
             f"lvaues typed in stub: {self._matched_stub_var_num}")

    @staticmethod
    def gen_csv_header():
        return "function," \
               "function in stub," \
               "distinct function in stub," \
               "function typed in source," \
               "matched function typed in corresponding stub file," \
               "function typed in corresponding stub file but not matched," \
               "function typed overload in corresponding stub file," \
               "function source file typed rate," \
               "function stub file typed rate," \
               "lvaues," \
               "typed lvaues in source," \
               "lvaues typed in stub\n"

    def gen_csv_line(self):
        return f"{self._fun_num}," \
               f"{self._stub_fun_num}," \
               f"{self._distinct_stub_fun}," \
               f"{self._typed_src_fun_num}," \
               f"{self._matched_stub_fun_num}," \
               f"{self._stubed_unsourced}," \
               f"{self._overload_stub_num}," \
               f"{self._typed_src_fun_num / self._fun_num}," \
               f"{self._matched_stub_fun_num / self._fun_num}," \
               f"{self._var_num}," \
               f"{self._typed_var_num}," \
               f"{self._matched_stub_var_num}\n"


class AssignCount(CsvItem):
    def __init__(self, name_count, subscript_count, attribute_count, tuple_count, list_count, slice_count,
                 typed_slice_count, typed_attribute_count, typed_subscript_count, typed_name_count,
                 typed_slice_assign_stub, typed_attribute_stub, typed_subscript_stub, typed_name_stub):
        self.name_count = name_count
        self.subscript_count = subscript_count
        self.attribute_count = attribute_count
        self.tuple_count = tuple_count
        self.list_count = list_count
        self.slice_count = slice_count
        self.typed_name_count = typed_name_count
        self.typed_subscript_count = typed_subscript_count
        self.typed_attribute_count = typed_attribute_count
        self.typed_slice_count = typed_slice_count
        self.typed_slice_assign_stub = typed_slice_assign_stub
        self.typed_attribute_stub = typed_attribute_stub
        self.typed_subscript_stub = typed_subscript_stub
        self.typed_name_stub = typed_name_stub

    def __str__(self):
        return (f"name assignment: {self.name_count}\n"
                f"subscript assignment: {self.subscript_count}\n"
                f"attribute assignment: {self.attribute_count}\n"
                f"tuple unpacking assignment: {self.tuple_count}\n"
                f"list unpacking assignment: {self.list_count}\n"
                f"slice assignment: {self.slice_count}")

    @staticmethod
    def gen_csv_header():
        return "name assignment,subscript assignment,attribute assignment," \
               "slice assignment," \
               "typed name assignment,typed subscript assignment,typed attribute assignment," \
               "typed slice assignment," \
               "typed name in stub," \
               "typed subscript in stub," \
               "typed attribute in stub," \
               "typed slice assign in stub\n"

    def gen_csv_line(self):
        return f"{self.name_count},{self.subscript_count},{self.attribute_count}," \
               f"{self.slice_count}," \
               f"{self.typed_name_count},{self.typed_subscript_count},{self.typed_attribute_count}," \
               f"{self.typed_slice_count}," \
               f"{self.typed_name_stub}," \
               f"{self.typed_subscript_stub}," \
               f"{self.typed_attribute_stub}," \
               f"{self.typed_slice_assign_stub}\n"


ONLYANY = "onlyAny"
TYPED = "typed"
UNTYPED = "untyped"


class FunCounterSingle(NodeVisitor):
    def __init__(self, tokens: asttokens.ASTTokens):
        self.tokens = tokens
        self.fun_num = 0
        self.typed_fun_num = 0
        self.fun_defs = []
        self.fun_set = set()
        self.typed_fun_set = set()
        self._nested_scope = []

        self.type_related_line = set()

        self._import_from_stack: List[Tuple[str, ast.ImportFrom]] = []
        self._import_stack: List[Tuple[str, ast.Import]] = []

        self.target_num = 0
        self.typed_target_num = 0
        self.typed_name_assign_target = set()

        self.containNotAny = False
        self.has_annotation = False

        # assignment target category
        # raw
        self._name = 0
        # a[b]
        self._subscript = 0
        # a.b
        self._attribute = 0
        # a, b = (x,y)
        self._tuple = 0
        # [N1, N2, N3] = [a.astype(float) for a in [M1, M2, M3]]
        self._list_assign = 0
        # a[a:b] = c
        self._slice_assign = 0

        self._typed_slice_assign = 0
        self._typed_attribute = 0
        self._typed_subscript = 0
        self._typed_name = 0

        # any rate
        self.annotation_num = 0
        self.any_num = 0

    def is_all_any_file(self) -> bool:
        return not self.containNotAny and self.has_annotation

    def is_typed_file(self) -> bool:
        return self.has_annotation

    def get_type_related_line(self, annotation: ast.expr):
        annotation_lines = set(range(annotation.lineno, annotation.end_lineno + 1))
        self.type_related_line.update(annotation_lines)
        type_text = self.tokens.get_text(annotation)
        related_ImportFroms = self.find_ImportFrom(type_text)
        related_Imports = self.find_Import(type_text)
        for related_ImportFrom in related_ImportFroms:
            self.type_related_line.add(related_ImportFrom.lineno)
        for related_Import in related_Imports:
            self.type_related_line.add(related_Import.lineno)

    def visit_ImportFrom(self, node: ImportFrom):
        for alias in node.names:
            self._import_from_stack.append((alias.asname if alias.asname is not None else alias.name, node))
        self.generic_visit(node)

    def visit_Import(self, node: Import):
        for alias in node.names:
            self._import_stack.append((alias.asname if alias.asname is not None else alias.name, node))
        self.generic_visit(node)

    def find_ImportFrom(self, type_text) -> List[ast.ImportFrom]:
        imported_name_lst = []
        related_import = []
        for imported_name, import_node in reversed(self._import_from_stack):
            if imported_name in type_text:
                if imported_name not in imported_name_lst:
                    related_import.append(import_node)
        return related_import

    def find_Import(self, type_text) -> List[ast.Import]:
        imported_name_lst = []
        related_import = []
        for imported_name, import_node in reversed(self._import_stack):
            if imported_name in type_text:
                if imported_name not in imported_name_lst:
                    related_import.append(import_node)
        return related_import

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        self._nested_scope.append(node.name)
        self.fun_num += 1
        is_typed_fun = False

        def is_typed_arg(an_arg) -> bool:
            res = False
            if an_arg.annotation is not None:
                self.annotation_num += 1
                self.get_type_related_line(an_arg.annotation)
                if isinstance(an_arg.annotation, Name) and an_arg.annotation.id == "Any":
                    self.any_num += 1
                res = True
            if an_arg.type_comment is not None:
                self.annotation_num += 1
                if an_arg.annotation.id == "Any":
                    self.any_num += 1
                res = True
            return res

        for an_arg in node.args.args:
            if is_typed_arg(an_arg):
                is_typed_fun = True

        for an_arg in node.args.kwonlyargs:
            if is_typed_arg(an_arg):
                is_typed_fun = True

        for an_arg in node.args.posonlyargs:
            if is_typed_arg(an_arg):
                is_typed_fun = True

        if node.args.kwarg is not None:
            an_arg = node.args.kwarg
            if is_typed_arg(an_arg):
                is_typed_fun = True

        if node.args.vararg is not None:
            an_arg = node.args.vararg
            if is_typed_arg(an_arg):
                is_typed_fun = True

        if node.returns is not None:
            self.annotation_num += 1
            if isinstance(node.returns, Name) and node.returns.id == "Any":
                self.any_num += 1
            is_typed_fun = True

        if is_typed_fun:
            self.has_annotation = True
            self.typed_fun_num += 1
            self.typed_fun_set.add(tuple(self._nested_scope))

        self.fun_defs.append(tuple(self._nested_scope))
        self.fun_set.add(tuple(self._nested_scope))
        self.generic_visit(node)
        self._nested_scope.pop()

    def visit_ClassDef(self, node: ClassDef) -> Any:
        self._nested_scope.append(node.name)
        self.generic_visit(node)
        self._nested_scope.pop()

    def visit_Assign(self, node: Assign) -> Any:
        for target in node.targets:
            self.target_num += 1
            if isinstance(target, ast.Name):
                self._name += 1
            elif isinstance(target, ast.Subscript):
                self._subscript += 1
            elif isinstance(target, ast.Attribute):
                self._attribute += 1
            elif isinstance(target, ast.Tuple):
                self._tuple += 1
            elif isinstance(target, ast.List):
                self._list_assign += 1
            elif isinstance(target, ast.Slice):
                self._slice_assign += 1
            else:
                print(type(target).__name__)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        self.target_num += 1
        self.typed_target_num += 1
        self.has_annotation = True
        self.get_type_related_line(node.annotation)
        self.annotation_num += 1
        if isinstance(node.target, ast.Name):
            self._name += 1
            self._typed_name += 1
            if tuple(self._nested_scope) + (self.tokens.get_text(node),) in self.typed_name_assign_target:
                print(tuple(self._nested_scope) + (self.tokens.get_text(node),))
            self.typed_name_assign_target.add(tuple(self._nested_scope) + (self.tokens.get_text(node),))

        elif isinstance(node.target, ast.Subscript):
            self._subscript += 1
            self._typed_subscript += 1
        elif isinstance(node.target, ast.Attribute):
            self._attribute += 1
            self._typed_attribute += 1
        elif isinstance(node.target, ast.List):
            self._list_assign += 1
        elif isinstance(node.target, ast.Slice):
            self._slice_assign += 1
            self._typed_slice_assign += 1
        else:
            print(type(node.target).__name__)
        if node.annotation is not None:
            if isinstance(node.annotation, Name) and node.annotation.id == "Any":
                self.any_num += 1
                self.containNotAny = True

        self.generic_visit(node)

    def assign_count(self):
        return self._name, self._subscript, self._attribute, self._tuple, self._list_assign, self._slice_assign, \
               self._typed_slice_assign, self._typed_attribute, self._typed_subscript, self._typed_name


class FunCoverageCalculator:
    def __init__(self, src_root: Path, stub_root: Path):
        self._fun_num: int = 0
        self._typed_fun_num = 0
        self._typed_src_fun_num = 0
        self._matched_stub_fun_num = 0
        self._stub_fun_num = 0
        self._target_num = 0
        self._typed_var_num = 0
        self._typed_src_target_num = 0
        self._matched_typed_stub_target_num = 0
        self._distinct_stub_fun = 0
        self.src_root = src_root
        self.stub_root = stub_root
        self._file_type_list: List[FileAttribute] = []
        self.not_match_fun_list: List[str] = []

        self.overload_dict_matched = defaultdict(int)
        self.overload_dict_all = defaultdict(int)

        self._typed_file = 0
        self._stubed_unsourced = 0
        self.overload_stub_matched_num = 0
        self.overload_stub_all_num = 0

        # assign category
        self.name_assign = 0
        self.subscript_assign = 0
        self.attribute_assign = 0
        self.tuple_assign = 0
        self.list_assign = 0
        self.slice_assign = 0

        self.typed_slice_assign = 0
        self.typed_attribute = 0
        self.typed_subscript = 0
        self.typed_name = 0

        self.typed_slice_assign_stub = 0
        self.typed_attribute_stub = 0
        self.typed_subscript_stub = 0
        self.typed_name_stub = 0

        self.annotation_num = 0
        self.any_num = 0

        self.type_manner = set()

        # type related line
        self._type_related_src_line = 0
        self._type_related_stub_line = 0

        self.type_related_lines: Set[str] = set()
        self.max_overload_matched = 0
        self.max_overload_matched_fun = None

        self.max_overload_all = 0
        self.max_overload_all_fun = None

    def cov_rate(self) -> CsvItem:
        return CsvItem({
            "annotation num": self.annotation_num,
            "any num": self.any_num,
            "typed file": self._typed_file,
            "function": self._fun_num,
            "typed function": self._typed_fun_num,
            "not matched function": len(self.not_match_fun_list),
            "matched stub typed function": self._matched_stub_fun_num,
            "function typed in corresponding stub file but not matched": self._stubed_unsourced,
            "different function typed overload in corresponding stub": self.overload_stub_matched_num,
            "lvalues": self._target_num,
            "inlined typed lvalue": self._typed_src_target_num,
            "stub typed lvalue": self._matched_typed_stub_target_num,
            "var num": self.name_assign,
            "typed var in source": self.typed_name,
            "typed var in stub": self.typed_name_stub,
            "typed var num": self._typed_var_num,
            "var coverage": self._typed_var_num / self.name_assign if self.name_assign != 0 else 0,
            "other assign target": self.slice_assign + self.list_assign + self.tuple_assign + self.attribute_assign + self.subscript_assign,
            "other assign target(typed)": self.typed_subscript + self.typed_attribute + self.typed_slice_assign +
                                          self.typed_subscript_stub + self.typed_attribute_stub + self.typed_slice_assign_stub})

    def type_related_line(self) -> CsvItem:
        return CsvItem({"type related line in source": self._type_related_src_line,
                        "type related line in stub": self._type_related_stub_line})

    def assign_category(self) -> AssignCount:
        return AssignCount(self.name_assign, self.subscript_assign, self.attribute_assign, self.tuple_assign,
                           self.list_assign, self.slice_assign,
                           self.typed_slice_assign, self.typed_attribute, self.typed_subscript, self.typed_name,
                           self.typed_slice_assign_stub,
                           self.typed_attribute_stub,
                           self.typed_subscript_stub,
                           self.typed_name_stub)

    def cal_cov(self, src: Path = None, stub: Path = None):
        if src is None:
            src = self.src_root
        if stub is None:
            stub = self.stub_root
        with os.scandir(src) as entries:
            for entry in entries:
                if entry.is_dir():
                    stub_dir_path = find(entry.name, stub)
                    if stub_dir_path is None:
                        self.fun_count(entry)
                    else:
                        self.cal_cov(entry, stub_dir_path)
                elif entry.name.endswith(".py"):
                    stub_file = find(entry.name[:-3] + ".pyi", stub)
                    if stub_file is None:
                        self.fun_count(entry)
                    else:
                        self.type_manner.add("stub")
                        self._fun_count_pair(Path(entry), stub_file)

    def fun_count(self, path: Path):
        if path.is_dir():
            with os.scandir(path) as entries:
                for entry in entries:
                    self.fun_count(entry)
        elif path.is_file() and path.name.endswith(".py"):
            self._fun_count_single(Path(path))

    def _fun_count_single(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                tokens = asttokens.ASTTokens(file.read(), True)
            except Exception:
                return
            tree = tokens.tree
            funCounter = FunCounterSingle(tokens)
            funCounter.visit(tree)
            self.srcResultProcess(funCounter)
            self.collectTypeRelatedLines(file_path.relative_to(self.src_root), funCounter)
            if funCounter.annotation_num == 0:
                file_type = UNTYPED
            elif funCounter.annotation_num == funCounter.any_num:
                file_type = ONLYANY
            else:
                file_type = TYPED
                self.type_manner.add("inline")
            self.annotation_num += funCounter.annotation_num
            self.any_num += funCounter.any_num
            self._file_type_list.append(FileAttribute(self.src_root, file_path, file_type,
                                                      funCounter.annotation_num, funCounter.any_num))

    def _fun_count_pair(self, src_path: Path, stub_path: Path):
        with open(src_path, "r", encoding="utf-8") as src_file:
            with open(stub_path, "r", encoding="utf-8") as stub_file:
                try:
                    src_tokens = asttokens.ASTTokens(src_file.read(), True)
                    stub_file_content = stub_file.read()
                    stub_tokens = asttokens.ASTTokens(stub_file_content, True)
                except SyntaxError:
                    return
                src_tree = src_tokens.tree
                stub_tree = stub_tokens.tree
                srcFunCounter = FunCounterSingle(src_tokens)
                stubFunCounter = FunCounterSingle(stub_tokens)
                srcFunCounter.visit(src_tree)
                stubFunCounter.visit(stub_tree)
                # stub related
                self.srcstubResultProcess(srcFunCounter, stubFunCounter)
                # print(stub_path)
                # print(stubFunCounter.fun_defs)
                self._stub_fun_num += stubFunCounter.fun_num
                self._matched_stub_fun_num += self.cal_stubed_funs(srcFunCounter, stubFunCounter, stub_path)
                self._matched_typed_stub_target_num += stubFunCounter.typed_target_num
                self._distinct_stub_fun += len(stubFunCounter.fun_set)
                # file type
                if stubFunCounter.annotation_num == 0 and srcFunCounter.annotation_num == 0:
                    file_type = UNTYPED
                elif stubFunCounter.annotation_num == stubFunCounter.any_num and \
                        srcFunCounter.annotation_num == srcFunCounter.any_num:
                    file_type = ONLYANY
                else:
                    file_type = TYPED

                self.annotation_num += srcFunCounter.annotation_num + stubFunCounter.annotation_num
                self.any_num += srcFunCounter.any_num + stubFunCounter.any_num

                self._file_type_list.append(FileAttribute(self.src_root, src_path, file_type,
                                                          stubFunCounter.annotation_num, stubFunCounter.any_num))
                self.collectTypeRelatedLines(src_path.relative_to(self.src_root), srcFunCounter)
                lines = stub_file_content.split('\n')
                for i in range(0, len(lines)):
                    tokens = lines[i].split()
                    if tokens:
                        if tokens[0][0] != '#':
                            self.collectTypeRelatedLine(stub_path.relative_to(self.stub_root), i + 1)

    def srcResultProcess(self, srcFunCounter):
        # source file
        self._fun_num += srcFunCounter.fun_num
        self._typed_fun_num += srcFunCounter.typed_fun_num
        self._typed_src_fun_num += srcFunCounter.typed_fun_num
        self._target_num += srcFunCounter.target_num
        self._typed_src_target_num += srcFunCounter.typed_target_num

        if srcFunCounter.is_typed_file():
            self._typed_file += 1

        a, b, c, d, e, f, g, h, i, j = srcFunCounter.assign_count()
        self.name_assign += a
        self.subscript_assign += b
        self.attribute_assign += c
        self.tuple_assign += d
        self.list_assign += e
        self.slice_assign += f

        self.typed_slice_assign += g
        self.typed_attribute += h
        self.typed_subscript += i
        self.typed_name += j

        self._type_related_src_line += len(srcFunCounter.type_related_line)

    def collectTypeRelatedLine(self, filePath: Path, lineno: int):
        self.type_related_lines.add("{0}::{1}".format(str(filePath), str(lineno)))

    def collectTypeRelatedLines(self, filePath: Path, funCounter: FunCounterSingle):
        for n in funCounter.type_related_line:
            self.type_related_lines.add("{0}::{1}".format(str(filePath), str(n)))

    def srcstubResultProcess(self, srcFunCounter: FunCounterSingle, stubFunCounter: FunCounterSingle):
        # source file
        self._fun_num += srcFunCounter.fun_num
        self._typed_src_fun_num += srcFunCounter.typed_fun_num
        self._target_num += srcFunCounter.target_num
        self._typed_src_target_num += srcFunCounter.typed_target_num

        self._typed_file += 1

        a, b, c, d, e, f, g, h, i, j = srcFunCounter.assign_count()
        self.name_assign += a
        self.subscript_assign += b
        self.attribute_assign += c
        self.tuple_assign += d
        self.list_assign += e
        self.slice_assign += f

        self.typed_slice_assign += g
        self.typed_attribute += h
        self.typed_subscript += i
        self.typed_name += j

        a, b, c, d, e, f, g, h, i, j = stubFunCounter.assign_count()
        self.typed_slice_assign_stub += g
        self.typed_attribute_stub += h
        self.typed_subscript_stub += i
        self.typed_name_stub += j
        distinct_typed_fun = srcFunCounter.typed_fun_set.union(stubFunCounter.typed_fun_set)
        self._typed_fun_num += len(distinct_typed_fun)
        distinct_typed_assign_target = srcFunCounter.typed_name_assign_target.union(
            stubFunCounter.typed_name_assign_target)
        self._typed_var_num += len(distinct_typed_assign_target)

        self._type_related_src_line += len(srcFunCounter.type_related_line)
        self._type_related_stub_line += len(stubFunCounter.type_related_line)

    def cal_stubed_funs(self, src_fun_counter: FunCounterSingle, stub_fun_counter: FunCounterSingle, stub: Path) -> int:
        src_funs = {x for x in src_fun_counter.fun_defs}
        stub_funs = {x for x in stub_fun_counter.typed_fun_set}
        inter = src_funs & stub_funs
        stubed_unsourced = stub_funs - src_funs
        for fun in stubed_unsourced:
            inner_scope = ""
            for scope in fun:
                inner_scope += "::" + scope
            self.not_match_fun_list.append(str(stub.relative_to(self.stub_root.parent)) + inner_scope)

        # if len(stubed_unsourced) != 0:
        #     print(stubed_unsourced)
        self._stubed_unsourced += len(stubed_unsourced)
        overloads_matched = {x: stub_fun_counter.fun_defs.count(x) for x in src_funs}
        if len(overloads_matched) != 0:
            max_overload_fun_match, overload_num_matched = max(overloads_matched.items(), key=lambda x: x[1])
            if overload_num_matched > self.max_overload_matched and overload_num_matched > 1:
                self.max_overload_matched = overload_num_matched
                inner_scope = ""
                for scope in max_overload_fun_match:
                    inner_scope += "::" + scope
                self.max_overload_matched_fun = str(stub.relative_to(self.stub_root.parent)) + inner_scope

        overload_all = {x: stub_fun_counter.fun_defs.count(x) for x in stub_funs}
        if len(overload_all) != 0:
            max_overload_fun_all, overload_num_all = max(overload_all.items(), key=lambda x: x[1])
            if overload_num_all > self.max_overload_all and overload_num_all > 1:
                self.max_overload_all = overload_num_all
                inner_scope = ""
                for scope in max_overload_fun_all:
                    inner_scope += "::" + scope
                self.max_overload_all_fun = str(stub.relative_to(self.stub_root.parent)) + inner_scope

        # function in source -> overload number
        # print(overloads)
        for key, value in overloads_matched.items():
            if value > 1:
                self.overload_dict_matched[value] += 1
        for key, value in overloads_matched.items():
            if value != 1 and key in inter:
                self.overload_stub_matched_num += 1

        for key, value in overload_all.items():
            if value > 1:
                self.overload_dict_all[value] += 1
                self.overload_stub_all_num += 1

        return len(inter)

    def get_file_attr(self) -> List[FileAttribute]:
        return self._file_type_list

    def file_type_dump(self, filename_postfix: str = "FileType.csv"):
        filename = self.src_root.name + filename_postfix
        with open(filename, "w") as file:
            file.write(FileAttribute.gen_csv_header())
            for item in self._file_type_list:
                file.write(item.gen_csv_line())
