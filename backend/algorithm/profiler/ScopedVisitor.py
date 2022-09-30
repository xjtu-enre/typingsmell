from ast import NodeVisitor, FunctionDef, ClassDef
from pathlib import Path
from typing import List


class ScopedVisitor(NodeVisitor):
    def __init__(self):
        self.scope: List[str] = []


    def visit(self, node):
        if isinstance(node, FunctionDef):
            self.scope.append(node.name)
            super(ScopedVisitor, self).visit(node)
            self.scope.pop()
        elif isinstance(node, ClassDef):
            self.scope.append(node.name)
            super(ScopedVisitor, self).visit(node)
            self.scope.pop()
        else:
            super(ScopedVisitor, self).visit(node)


