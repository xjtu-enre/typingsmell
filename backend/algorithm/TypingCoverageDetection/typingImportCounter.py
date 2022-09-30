import ast
import os
import sys
from ast import NodeVisitor, ImportFrom, Import, List, Tuple, Attribute, Name, AnnAssign, FunctionDef
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

import asttokens

from algorithm.TypingCoverageDetection.CsvItem import CsvItem, union_csv_items
from algorithm.TypingCoverageDetection.Util import find
from algorithm.TypingCoverageDetection.filecoveragecalculator import ProjeceName


class ImportDepCounterSingle(NodeVisitor):
    def __init__(self, tokens, file_path: Path, root: Path):
        # file_path: relative path from root of project
        self.root = root
        self.src_path = file_path
        self.tokens: asttokens.ASTTokens = tokens
        self._import_from_stack: List[Tuple[str, ast.ImportFrom]] = []
        self._import_stack: List[Tuple[str, ast.Import]] = []
        self.typing_import_num = 0
        self.other_import_num = 0
        self.typing_imports_use = defaultdict(int)
        self.import_target_set = set()
        self.Literal_use = 0

        self.imported_name_from_typing = set()
        self.imported_name_count = defaultdict(int)

    def visit_ImportFrom(self, node: ImportFrom):
        for alias in node.names:
            self._import_from_stack.append(
                (alias.name, node) if alias.asname is None else (alias.asname, node, alias.name))

        self.generic_visit(node)

    def visit_Import(self, node: Import):
        for alias in node.names:
            self._import_stack.append((alias.name, node) if alias.asname is None else (alias.asname, node, alias.name))
        self.generic_visit(node)

    def find_ImportFrom(self, type_text):
        imported_name_lst = []
        related_imports: List[Tuple[str, ImportFrom]] = []
        importfrom_nodes_typing = set()
        importfrom_nodes_other = set()
        for imported_name, *import_from_node in reversed(self._import_from_stack):
            if imported_name in type_text and imported_name not in imported_name_lst:
                imported_name_lst.append(imported_name)
                if import_from_node[0].module == "typing":
                    importfrom_nodes_typing.add(import_from_node[0])

                    self.typing_imports_use[imported_name if len(import_from_node) == 1 else import_from_node[1]] \
                        += type_text.count(imported_name)
                else:
                    importfrom_nodes_other.add(import_from_node[0])
                    if import_from_node[0].module is not None:
                        self.import_target_set.add(self.module2file(import_from_node[0].module))
        self.typing_import_num += len(importfrom_nodes_typing)
        self.other_import_num += len(importfrom_nodes_other)

        return related_imports

    def find_Import(self, type_text):
        imported_name_lst = []
        import_nodes_typing = set()
        import_nodes_other = set()
        related_imports: List[Tuple[str, ast.Import]] = []
        for imported_name, *import_node in reversed(self._import_stack):
            if imported_name in type_text and imported_name not in imported_name_lst:
                imported_name_lst.append(imported_name)
                if imported_name == "typing":
                    import_nodes_typing.add(import_node[0])
                    self.typing_imports_use["typing"] += type_text.count("typing")
                else:
                    import_nodes_other.add(import_node[0])
                    self.import_target_set.add(self.module2file(imported_name))
                related_imports.append((imported_name, import_node[0]))

        self.typing_import_num += len(import_nodes_typing)
        self.other_import_num += len(import_nodes_other)
        return related_imports

    def visit_Attribute(self, node: Attribute) -> Any:
        if isinstance(node.value, Name) and node.value.id == "typing":
            self.typing_imports_use[node.attr] += 1

        self.generic_visit(node)

    def find_dep_of_annotation(self, annotation: ast.expr):
        type_text = self.tokens.get_text(annotation)
        self.Literal_use += type_text.count("Literal")
        self.find_Import(type_text)
        self.find_ImportFrom(type_text)

    def visit_FunctionDef(self, node: FunctionDef) -> Any:

        def find_arg_deps(an_arg):
            if an_arg.annotation is not None:
                self.find_dep_of_annotation(an_arg.annotation)

        for an_arg in node.args.args:
            find_arg_deps(an_arg)

        for an_arg in node.args.kwonlyargs:
            find_arg_deps(an_arg)

        for an_arg in node.args.posonlyargs:
            find_arg_deps(an_arg)

        if node.args.kwarg is not None:
            an_arg = node.args.kwarg
            find_arg_deps(an_arg)

        if node.args.vararg is not None:
            an_arg = node.args.vararg
            find_arg_deps(an_arg)

        if node.returns is not None:
            type_text = self.tokens.get_text(node.returns)
            self.Literal_use += type_text.count("Literal")
            self.find_Import(type_text)
            self.find_ImportFrom(type_text)

        self.generic_visit(node)

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        if node.annotation is not None:
            self.find_dep_of_annotation(node.annotation)

        self.generic_visit(node)

    def module2file(self, module: str):
        file_path = Path(self.src_path)
        file_path = file_path.parent.parent
        elems = module.split(".")
        if module[0] == '.':
            module = module[1:]
        relative_path = module.replace(".", "\\")
        if file_path.joinpath(elems[0]).exists() or file_path.joinpath(elems[0] + ".py").exists():
            if file_path.joinpath(Path(relative_path)).is_dir():
                return file_path.joinpath(Path(relative_path)).joinpath("__init__.py")
            elif file_path.joinpath(Path(relative_path + ".py")).exists():
                return file_path.joinpath(Path(relative_path + ".py"))

        while (not file_path.joinpath(relative_path).exists()) and file_path != self.root.parent:
            file_path = file_path.parent
            if file_path.joinpath(Path(relative_path)).is_dir():
                return file_path.joinpath(Path(relative_path)).joinpath("__init__.py")
            elif file_path.joinpath(Path(relative_path + ".py")).exists():
                return file_path.joinpath(Path(relative_path + ".py"))

        return None


class TypingDepsCounter:

    def __init__(self, src_root: Path):
        self.src_root = src_root
        self.typing_import_num: int = 0
        self.other_import_num: int = 0
        self.typing_imports_use: Dict[str, int] = defaultdict(int)
        self.import_target_set = set()
        self.Literal_use = 0

    def cal_import_deps_single(self, file_path: Path, src_path: Path):
        with open(file_path, "r", encoding="utf-8") as file:
            tokens = asttokens.ASTTokens(file.read(), parse=True)
            importCounter = ImportDepCounterSingle(tokens, src_path, self.src_root)
            importCounter.visit(tokens.tree)
            self.typing_import_num += importCounter.typing_import_num
            self.other_import_num += importCounter.other_import_num
            if len(importCounter.import_target_set) != 0:
                print(importCounter.import_target_set)
            for key, value in importCounter.typing_imports_use.items():
                if key not in self.typing_imports_use:
                    self.typing_imports_use[key] = value
                else:
                    self.typing_imports_use[key] += value

    def cal_import_deps(self, src: Path, stub: Path):
        with os.scandir(src) as entries:
            for entry in entries:
                if entry.is_dir():
                    stub_dir_path = find(entry.name, stub)
                    self.cal_import_deps(entry, stub_dir_path)
                elif entry.name.endswith(".py"):
                    stub_file = find(entry.name[:-3] + ".pyi", stub)
                    if stub_file is None:
                        self.cal_import_deps_single(Path(entry), Path(entry))
                    else:
                        self.cal_import_deps_single(Path(entry), Path(entry))
                        self.cal_import_deps_single(stub_file, Path(entry))

    def get_import_deps(self):
        ret = {"typing import": self.typing_import_num,
               "other typing import": self.other_import_num}
        ret.update(self.typing_imports_use)
        return CsvItem(ret)

    def get_usage(self):
        return self.typing_imports_use


if __name__ == '__main__':
    argv = sys.argv[1:]
    src_dir = Path(argv[0])
    stub_dir = Path(argv[1])
    if len(argv) > 2:
        project_name = argv[2]
    else:
        project_name = src_dir.name
    print(f"\nstart checking project {project_name} usage")
    project_name_item = ProjeceName(project_name)
    tdc = TypingDepsCounter(src_dir.parent)
    tdc.cal_import_deps(src_dir, stub_dir)
    tdc.get_import_deps()
    print(tdc.typing_import_num)
    print(tdc.typing_imports_use)
    with open(project_name + "ImportDependency.csv", "w") as file:
        file.write(union_csv_items(project_name_item, tdc.get_import_deps()))

    print(f"project {project_name} checked")
