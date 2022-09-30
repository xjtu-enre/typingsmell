import os
import re
import sys
from ast import NodeVisitor, ClassDef, FunctionDef
from functools import total_ordering
from pathlib import Path
from typing import Tuple, Set, List

from asttokens import asttokens

from algorithm.TypingCoverageDetection.CsvItem import CsvItem
from algorithm.TypingCoverageDetection.Util import find


class ClassSignature:
    def __init__(self, rel_file_path, nested_scope: Tuple[str], bases: Set[str]):
        self.nested_scope = nested_scope
        self.bases = bases
        self.rel_file_path = rel_file_path

    def __hash__(self):
        return hash(self.nested_scope)

    def __eq__(self, other):
        if isinstance(other, ClassSignature):
            return other.nested_scope == self.nested_scope
        return False

    def __str__(self):
        res = str(self.rel_file_path).replace("\\", "/")
        for scope in self.nested_scope:
            res += "::" + scope
        return res

    def name(self) -> str:
        return self.nested_scope[-1]


class ClassCounterSingle(NodeVisitor):
    def __init__(self, tokens: asttokens.ASTTokens, rel_path):
        self.tokens = tokens
        self.class_num = 0
        self.new_class_num: int = 0
        self.new_class_inherit: int = 0
        self.class_sigs: Set[ClassSignature] = set()
        self.implicit_impls = set()
        self.explicit_impls = set()
        self.rel_file_path = rel_path
        # self.root = root
        # self.file_path = file_path
        self.nested_scope: List[str] = []

    def visit_ClassDef(self, node: ClassDef):
        self.nested_scope.append(node.name)
        bases: Set[str] = set()
        for base in node.bases:
            type_text = self.tokens.get_text(base)
            bases.add(type_text)
        self.class_sigs.add(ClassSignature(self.rel_file_path, tuple(self.nested_scope), bases))
        self.generic_visit(node)
        self.nested_scope.pop()

    def visit_FunctionDef(self, node: FunctionDef):
        self.nested_scope.append(node.name)
        self.generic_visit(node)
        self.nested_scope.pop()

    def collectClass(self):
        self.visit(self.tokens.tree)


@total_ordering
class SubtypeRel:
    def __init__(self, subClass: ClassSignature, superClass: ClassSignature):
        self.superClass = superClass
        self.subClass = subClass

    def __str__(self):
        return str(self.subClass) + "<:" + str(self.superClass)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)


def getNewClass(srcClasseCounter: ClassCounterSingle, stubClassesCounter: ClassCounterSingle) -> Set[ClassSignature]:
    return stubClassesCounter.class_sigs - srcClasseCounter.class_sigs


def getSubTypeRel(superClasses: Set[ClassSignature], classes: Set[ClassSignature]) -> Set[SubtypeRel]:
    res: Set[SubtypeRel] = set()
    for superClass in superClasses:
        for a_class in classes:
            for base in a_class.bases:
                if superClass.name() in base:
                    res.add(SubtypeRel(a_class, superClass))
                    break
    return res


def match_type(superName: str, base: str):
    regexp = re.compile(f'\\.{superName}$')
    return base == superName or regexp.search(base)


class ClassCounter:
    def __init__(self, src_dir: Path, stub_dir: Path, project_name=None):
        if project_name is None:
            project_name = src_dir.name
        self.project_name = project_name
        self.src_dir = src_dir
        self.stub_dir = stub_dir
        self.class_num = 0
        self.class_set: Set[ClassSignature] = set()
        self.new_class_set: Set[ClassSignature] = set()
        self.new_class_inherit_set: Set[SubtypeRel] = set()
        self.stub_classes: Set[ClassSignature] = set()

    def cal_class_use(self, src: Path = None, stub: Path = None):
        if src is None:
            src = self.src_dir
        if stub is None:
            stub = self.stub_dir

        with os.scandir(src) as entries:
            for entry in entries:
                if entry.is_dir():
                    stub_dir_path = find(entry.name, stub)
                    if stub_dir_path is None:
                        self.class_count(Path(entry))
                    else:
                        self.cal_class_use(Path(entry), stub_dir_path)
                elif entry.name.endswith(".py"):
                    stub_file = find(entry.name[:-3] + ".pyi", stub)
                    if stub_file is None:
                        self.class_count(Path(entry))
                    else:
                        self.class_count_pair(Path(entry), stub_file)

    def new_classes_item(self) -> CsvItem:
        self.cal_class_use()
        return CsvItem({"unmatched classes": len(self.new_class_set),"classes in stub": len(self.stub_classes)})

    def class_count(self, path: Path):
        if path.is_dir():
            with os.scandir(path) as entries:
                for entry in entries:
                    self.class_count(Path(entry))
        elif path.is_file() and path.name.endswith(".py"):
            self.class_count_single(Path(path))

    def class_count_single(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as file:
            tokens = asttokens.ASTTokens(file.read(), parse=True)
            classCounter = ClassCounterSingle(tokens, file_path.relative_to(self.src_dir.parent))
            classCounter.collectClass()
            self.class_set.update(classCounter.class_sigs)

    def class_count_pair(self, src_path: Path, stub_path: Path):
        with open(src_path, "r", encoding="utf-8") as src_file:
            with open(stub_path, "r", encoding="utf-8") as stub_file:
                src_tokens = asttokens.ASTTokens(src_file.read(), True)
                stub_tokens = asttokens.ASTTokens(stub_file.read(), True)
                srcClassCounter = ClassCounterSingle(src_tokens, src_path.relative_to(self.src_dir.parent))
                stubClassCounter = ClassCounterSingle(stub_tokens, stub_path.relative_to(self.stub_dir.parent))
                srcClassCounter.collectClass()
                stubClassCounter.collectClass()
                self.class_set.update(srcClassCounter.class_sigs)
                stub_classes = stubClassCounter.class_sigs
                self.stub_classes.update(stub_classes)
                self.class_set.update(stub_classes)
                newClasses = getNewClass(srcClassCounter, stubClassCounter)
                self.new_class_set.update(newClasses)
                self.new_class_inherit_set.update(getSubTypeRel(newClasses, stub_classes))

    def dump_new_class(self, project_name, cal_path):
        if len(self.new_class_set) != 0:
            with open(f"{cal_path}/{project_name}/NewClasses.csv", "w", encoding="utf-8") as file:
                for new_class in self.new_class_set:
                    file.write(str(new_class) + "\n")

    def dump_sub_class_rel(self, project_name, cal_path):
        if len(self.new_class_inherit_set) != 0:
            with open(f"{cal_path}/{project_name}/NewClassInherit.csv", "w", encoding="utf-8") as file:
                for new_class_inherit in sorted(self.new_class_inherit_set):
                    file.write(f"{new_class_inherit.superClass},{new_class_inherit.subClass}\n")


if __name__ == '__main__':
    argv = sys.argv[1:]
    src_dir = Path(argv[0])
    stub_dir = Path(argv[1])
    output_path = "./"  #
    if len(argv) > 2:
        project_name = argv[2]
    else:
        project_name = src_dir.name
    print(f"\nstart counting class use of project {project_name}")
    classCounter = ClassCounter(src_dir, stub_dir)
    classCounter.cal_class_use()
    classCounter.dump_new_class(project_name, cal_path=output_path)
    classCounter.dump_sub_class_rel(project_name, cal_path=output_path)
