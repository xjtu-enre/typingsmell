import os
from pathlib import Path
from typing import Tuple
from flask import send_file


class EntityType:
    Function = "Function"
    Class = "Class"
    Variable = "Variable"
    StubFile = "StubFile"
    IfStmt = "IfStmt"


class ImplEntityType:
    TypedFunction = "TypedFunction"
    Annotation = "Annotation"
    IfStmt = "IfStmt"
    ClassDef = "ClassDef"


class Entity:
    def __init__(self, entitytype: EntityType, file: Path, startline, endline, startcol, endcol) -> None:
        self.entitytype = entitytype
        self.file = file
        self.startline = startline
        self.endline = endline
        self.startcol = startcol
        self.endcol = endcol


class ComplexPattern:
    APIVis = "ApiVisibility"
    BaseClass = "BaseclassPresentation"
    ExtensionTyping = "ExtensionTyping"
    OverloadTyping = "Overload"
    TypeCompatibility = "TypeCompatibility"
    FunctionalVar = "FunctionalVariable"
    GetAttrDef = "__getattr__Def"
    NotPattern = ""


class TypeImplementEntity:
    def __init__(self, impltype: ImplEntityType, file: Path, startline, endline, startcol, endcol) -> None:
        self.impltype = impltype
        self.file = file
        self.startline = startline
        self.endline = endline
        self.startcol = startcol
        self.endcol = endcol


class TypedEntity:
    def __init__(self, entity_type: str, file: Path, scope: Tuple, lineno: int, end_lineno: int, pattern: str):
        self.entity_type = entity_type
        self.file = file
        self.scope = scope
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.pattern = pattern

    def __str__(self) -> str:
        res = str(self.file)
        for name in self.scope:
            res += f"::{name}"
        res += f",{self.pattern},{str(self.file)},{self.entity_type},{self.lineno},{self.end_lineno},"
        return res

    def toCsv(self, project_path: str) -> str:
        project_name = project_path.rsplit('/', 1)[1]
        file_path = str(self.file)
        file_path = file_path.replace("\\", '/').rsplit(project_name + '/', 1)[1]
        res = str(self.file)
        for name in self.scope:
            res += f"::{name}"
        res += f",{self.pattern},{file_path},{self.entity_type},{self.lineno},{self.end_lineno},"
        return res

    def toJson(self, project_path: str) -> dict:
        project_name = project_path.rsplit('/', 1)[1]
        file_path = str(self.file)
        file_path = file_path.replace("\\", '/').rsplit(project_name + '/', 1)[1]

        return {"entity_type": self.entity_type,
                "file_path": file_path,
                "start_line": self.lineno,
                "end_line": self.end_lineno
                }
