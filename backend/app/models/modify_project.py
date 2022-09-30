from typing import Dict, Any
from app.daos import session_commit
from app.daos.model import Project
from app.daos.project import DaoProject
from app.models.errors import PropertyNotExist


class ModifyProj:
    _project: Project
    _data: Dict[str, Any]
    _dao_project: DaoProject

    def __init__(self, project, data):
        self._data = data
        self._dao_project = DaoProject()
        self._project = project
        self._handle_dict()
        self._commit()

    def _handle_dict(self):
        for key, val in self._data.items():
            method = getattr(self, f'handle_{key}', None)
            if method is None:
                raise PropertyNotExist(f'{key} 属性不存在')
            method(val)

    def handle_encode_name(self, encode_name):
        self._project.encode_name = encode_name

    def handle_version(self, version):
        self._project.version = version

    def handle_file(self, file):
        self._project.file = file

    def handle_loc(self, loc):
        self._project.loc = loc

    def handle_type_manner(self, type_manner):
        self._project.type_manner = type_manner

    def handle_code_url(self, code_url):
        self._project.code_url = code_url

    def handle_star(self, star):
        self._project.star = star

    def handle_name(self, name):
        self._project.name = name

    def handle_step(self, step):
        self._project.step = step

    def _commit(self):
        session_commit()


def modify_project(project, data) -> ModifyProj.__class__:
    return ModifyProj(project, data)
