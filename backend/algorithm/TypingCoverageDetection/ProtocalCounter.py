import os
import sys
from ast import NodeVisitor, FunctionDef
from enum import Enum
from pathlib import Path
from typing import Set, Tuple

from asttokens import asttokens
from ast import ClassDef
from algorithm.TypingCoverageDetection.CsvItem import CsvItem, cat_csv_item
from algorithm.TypingCoverageDetection.Util import find


class ClassRel(Enum):
    ImplicitImpl = 0
    ExplicitImpl = 1
    NoRelation = 2


class Structural:
    def __init__(self, node: ClassDef, tokens: asttokens.ASTTokens, rel_class_path: Tuple, rel_file_path: Path):
        self._class_name = node.name
        self.bases = set()
        self.method_set = set()
        self.abstract_method_set = set()
        self.rel_path = rel_class_path
        self.rel_file_path = rel_file_path
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                decorator_text = tokens.get_text(stmt.decorator_list)
                self.method_set.add(stmt.name)

        for base in node.bases:
            self.bases.add(tokens.get_text(base))

    def add_method(self, method: str):
        self.method_set.add(method)

    def structural_name(self):
        return self._class_name

    def relation_with(self, rhs: 'Structural') -> ClassRel:
        if self._class_name in rhs.bases:
            return ClassRel.ExplicitImpl
        for method in self.method_set:
            if method not in rhs.method_set:
                return ClassRel.NoRelation
        if len(self.method_set) != 0:
            return ClassRel.ImplicitImpl
        else:
            return ClassRel.NoRelation

    def __str__(self):
        ret = str(self.rel_file_path)
        for e in self.rel_path:
            ret += "::" + str(e)
        return ret


class ProtocolCounterSingle(NodeVisitor):
    def __init__(self, tokens: asttokens.ASTTokens, rel_path):
        self.tokens = tokens
        self.protocol_num = 0
        self.protocol_impl_implicit: int = 0
        self.protocol_impl_explicit: int = 0
        self.protocols: Set[Structural] = set()
        self.class_defs: Set[Structural] = set()
        self.implicit_impls = set()
        self.explicit_impls = set()
        self.rel_file_path = rel_path
        # self.root = root
        # self.file_path = file_path
        self.nested_scope = []

    def visit_ClassDef(self, node: ClassDef):
        self.nested_scope.append(node.name)
        is_protocol = False
        for base in node.bases:
            type_text = self.tokens.get_text(base)
            if "Protocol" in type_text:
                self.protocols.add(Structural(node, self.tokens, tuple(self.nested_scope), self.rel_file_path))
                is_protocol = True
                break
        if not is_protocol:
            self.class_defs.add(Structural(node, self.tokens, tuple(self.nested_scope), self.rel_file_path))
        self.generic_visit(node)
        self.nested_scope.pop()

    def visit_FunctionDef(self, node: FunctionDef):
        self.nested_scope.append(node.name)
        self.generic_visit(node)
        self.nested_scope.pop()

    def workflow(self):
        self.collectClass()
        self.countRelation()

    def collectClass(self):
        self.visit(self.tokens.tree)

    def countRelation(self):
        self.protocol_num = len(self.protocols)
        for structural in self.protocols:
            for class_def in self.class_defs:
                relation = structural.relation_with(class_def)
                if relation == ClassRel.ExplicitImpl:
                    self.explicit_impls.add(class_def)
                    self.protocol_impl_explicit += 1
                elif relation == ClassRel.ImplicitImpl:
                    self.implicit_impls.add(class_def)
                    self.protocol_impl_implicit += 1


class ProtocolCounter:
    def __init__(self, src_dir: Path, stub_dir: Path):
        self.src_dir = src_dir
        self.stub_dir = stub_dir
        self.protocol_num = 0
        self.protocol_impl_implicit = 0
        self.protocol_impl_explict = 0
        self.protocol_set = set()
        self.protocol_implicit_set = set()
        self.protocol_explicit_set = set()

    def cal_protocol_use(self, src: Path = None, stub: Path = None):
        if src is None:
            src = self.src_dir
        if stub is None:
            stub = self.stub_dir

        with os.scandir(src) as entries:
            for entry in entries:
                if entry.is_dir():
                    stub_dir_path = find(entry.name, stub)
                    if stub_dir_path is None:
                        self.protocol_count(Path(entry))
                    else:
                        self.cal_protocol_use(Path(entry), stub_dir_path)
                elif entry.name.endswith(".py"):
                    stub_file = find(entry.name[:-3] + ".pyi", stub)
                    if stub_file is None:
                        self.protocol_count(Path(entry))
                    else:
                        self._protocol_count_pair(Path(entry), stub_file)

    def protocol_count(self, path: Path):
        if path.is_dir():
            with os.scandir(path) as entries:
                for entry in entries:
                    self.protocol_count(Path(entry))
        elif path.is_file() and path.name.endswith(".py"):
            self._protocol_count_single(Path(path))

    def _protocol_count_single(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as file:
            tokens = asttokens.ASTTokens(file.read(), parse=True)
            protocolCounter = ProtocolCounterSingle(tokens, file_path.relative_to(self.src_dir.parent))
            protocolCounter.workflow()
            self.protocol_num += protocolCounter.protocol_num
            self.protocol_impl_implicit += protocolCounter.protocol_impl_implicit
            self.protocol_impl_explict += protocolCounter.protocol_impl_explicit
            self.protocol_set.update(protocolCounter.protocols)
            self.protocol_implicit_set.update(protocolCounter.implicit_impls)
            self.protocol_explicit_set.update(protocolCounter.explicit_impls)

    def _protocol_count_pair(self, src_path: Path, stub_path: Path):
        with open(src_path, "r", encoding="utf-8") as src_file:
            with open(stub_path, "r", encoding="utf-8") as stub_file:
                src_tokens = asttokens.ASTTokens(src_file.read(), True)
                stub_tokens = asttokens.ASTTokens(stub_file.read(), True)
                srcProtocolCounter = ProtocolCounterSingle(src_tokens, src_path.relative_to(self.src_dir.parent))
                stubProtocolCounter = ProtocolCounterSingle(stub_tokens, stub_path.relative_to(self.stub_dir.parent))
                srcProtocolCounter.workflow()
                stubProtocolCounter.workflow()
                self.protocol_num += srcProtocolCounter.protocol_num
                self.protocol_impl_implicit += srcProtocolCounter.protocol_impl_implicit
                self.protocol_impl_explict += srcProtocolCounter.protocol_impl_explicit
                self.protocol_num += stubProtocolCounter.protocol_num
                self.protocol_impl_implicit += stubProtocolCounter.protocol_impl_implicit
                self.protocol_impl_explict += stubProtocolCounter.protocol_impl_explicit
                self.protocol_set.update(srcProtocolCounter.protocols, stubProtocolCounter.protocols)
                self.protocol_implicit_set.update(srcProtocolCounter.implicit_impls, stubProtocolCounter.implicit_impls)
                self.protocol_explicit_set.update(srcProtocolCounter.explicit_impls, stubProtocolCounter.explicit_impls)

    def dump_protocols(self):
        if len(self.protocol_set) != 0:
            with open(f"{project_name}Protocols.csv", "w", encoding="utf-8") as file:
                for protocol in self.protocol_set:
                    file.write(str(protocol) + "\n")
        if len(self.protocol_implicit_set) != 0:
            with open(f"{project_name}ProtocolsImplicit.csv", "w", encoding="utf-8") as file:
                for implicit in self.protocol_implicit_set:
                    file.write(str(implicit) + "\n")
        if len(self.protocol_explicit_set) != 0:
            with open(f"{project_name}ProtocolsExplicit.csv", "w", encoding="utf-8") as file:
                for explicit in self.protocol_explicit_set:
                    file.write(str(explicit) + "\n")


if __name__ == '__main__':
    argv = sys.argv[1:]
    src_dir = Path(argv[0])
    stub_dir = Path(argv[1])
    if len(argv) > 2:
        project_name = argv[2]
    else:
        project_name = src_dir.name
    print(f"\nstart counting protocol use of project {project_name}")
    protocolCounter = ProtocolCounter(src_dir, stub_dir)
    protocolCounter.cal_protocol_use()
    csv_item = CsvItem({"project": project_name,
                        "protocol use": protocolCounter.protocol_num,
                        "protocol implicit impl": protocolCounter.protocol_impl_implicit,
                        "protocol explicit impl": protocolCounter.protocol_impl_explict})
    csv_content = cat_csv_item([csv_item])
    with open(project_name + "ProtocolCount.csv", "w", encoding="utf-8") as file:
        file.write(csv_content)

    protocolCounter.dump_protocols()
