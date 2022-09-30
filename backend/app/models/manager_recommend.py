from app.daos.project import DaoProject
from algorithm.pratice import Recommend
from app.models.errors import ProjectNotFound


class IManagerRec:

    def get_recommend(self, project_id, feature, top):
        raise NotImplementedError()


class ManagerRec(IManagerRec):
    def get_recommend(self, project_id, feature, top):
        project = DaoProject().query_project_by_id(project_id)
        if project is None:
            raise ProjectNotFound
        return Recommend().handle_get_recommend(project.encode_name, feature, top)
