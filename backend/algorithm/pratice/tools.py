import os
from app.models.errors import EnreRunError


class Tool:
    project_path = './assets/projects/'
    output_path = "./assets/calculation/"
    dependency_dir = "-out/"
    dependency_tail = '_default_all_dep.json'

    @classmethod
    def use_enre(cls, project_name):
        if os.path.exists(cls.output_path + project_name) is True:
            if os.path.exists(
                    cls.output_path + project_name + '/' + project_name + cls.dependency_dir + project_name +
                    cls.dependency_tail):
                return
        else:
            os.makedirs(cls.output_path + project_name)
        enre_command = 'cd {0} && java -jar ../../../enre-type2.0.jar python {1} null {2}'.format(
            cls.output_path + project_name, '../../projects/' + project_name, project_name)
        res = os.system(enre_command)
        if res == 0:
            return
        else:
            raise EnreRunError('依赖分析错误')
