import os
import warnings
from typing import List
import git
from app.daos.project import DaoProject
from app.utils import DealFile
from app.models.modify_project import modify_project
from app.models.errors import ProjectNotFound, NetWorkError, FileReadError


class ProjectListRes:
    def __init__(self, res, count):
        self.res = res
        self.count = count


class IManagerFile:
    _project_id: int
    _project_path: str
    _manager: DaoProject

    def __init__(self):
        self._project_path = "/assets/projects/"
        self._manager = DaoProject()

    def get_project_path(self, path) -> List:
        raise NotImplementedError()

    # use system cmd
    def fetch_from_git(self, git_mirror, path):
        raise NotImplementedError()

    def get_file_text(self, project_id, file_path):
        raise NotImplementedError()

    def fetch_project(self, git_mirror, repo_path):
        raise NotImplementedError()


class ManagerFile(IManagerFile):

    def get_project_path(self, path) -> List:
        return DealFile().get_dirs(path)

    def fetch_from_git(self, git_source, path):
        warnings.warn("please use fetch_project(...)", DeprecationWarning)
        project = self._manager.query_project_by_repository(git_source + path)
        if project is None:
            project_path, project_name, encode_name = DealFile().git_fetch(git_source + path)
            self._manager.add_project(name=project_name, encode_name=encode_name, code_url=git_source + path)
            project = self._manager.query_project_by_encode_name(encode_name)
        elif project.encode_name is None or project.encode_name == '':  # !!!!
            _, _, encode_name = DealFile().git_fetch(git_source + path)
            modify_project(project, {'encode_name': encode_name})
        else:
            if os.path.exists('./assets/projects/' + project.encode_name) is not True:
                print("更新项目")
                _, _, encode_name = DealFile().git_fetch(git_source + path)
                modify_project(project, {'encode_name': encode_name})
            else:
                pass
        return project

    def get_file_text(self, project_id, file_path):
        project = self._manager.query_project_by_id(project_id)
        if project is None:
            raise ProjectNotFound('Project Not Found')
        # if project.encode_name is None or project.encode_name == '':
        #     if project.code_url != '':
        #         _, _, encode_project_name = DealFile().git_fetch(project.code_url)
        #         modify_project(project, {"encode_name": encode_project_name})
        #     else:
        #         raise ProjectNotFound('Project Not Found')
        project_path = os.getcwd() + self._project_path + project.encode_name + '/' + file_path
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                to_front_file = f.read()
        except Exception:
            raise FileReadError('File Read Error')
        return str(to_front_file)

    def fetch_project(self, git_url, repo_path):
        repo_url = git_url + repo_path
        project = self._manager.query_project_by_repository(repo_url)
        if project is None:
            # 新添加项目
            project_name = repo_path.strip('/').split('/', 1)[1]
            self._manager.add_project(name=f"{project_name}(uncloned)", code_url=repo_url)
            _, project_name, encode_name, commit_head = DealFile().git_fetch_re(git_url, repo_path)
            project = self._manager.query_project_by_repository(repo_url)
            modify_project(project, {'name': project_name, 'encode_name': encode_name, 'version': commit_head})
        elif project.encode_name is None or project.encode_name == '':
            # 添加完项目实际进行克隆
            _, project_name, encode_name, commit_head = DealFile().git_fetch_re(git_url, repo_path)
            modify_project(project, {'name': project_name, 'encode_name': encode_name, 'version': commit_head})
        else:
            _, _, encode_name, commit_head = DealFile().git_fetch_re(git_url, repo_path, project.version)
        project = self._manager.query_project_by_repository(repo_url)
        return project
