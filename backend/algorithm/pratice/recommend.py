from __future__ import division
from typing import List, Dict, Any

from algorithm.DegreeCentrality.recommender import recommend_by_degree, recommend_by_maintenance, recommend_by_drh
from algorithm.MaintenanceCostMeasurement.gitlogprocessor import *


class RecommendData:
    def __init__(self, degree_centrality: List = None, design_rule_hierarchy: List = None,
                 maintenance_cost: List = None, union: List = None, intersection: List = None):
        self.DegreeCentrality = degree_centrality
        self.DesignRuleHierarchy = design_rule_hierarchy
        self.MaintenanceCost = maintenance_cost
        self.Union = union
        self.Intersection = intersection


class Recommend:
    project_path = './assets/projects/'
    output_path = "./assets/calculation/"
    dep_tail = '_default_all_dep.json'

    @classmethod
    def handle_get_recommend(cls, project_name: str, features: List[str] = None,
                             top: List[str] = None):
        src_dir = Path(cls.project_path + project_name)
        rank_rates: List[float]
        default_rate = 0.1
        if top is not None:
            rank_rates = [float(x) * 0.01 for x in top]
        else:
            rank_rates = []
        if features is None:
            features = ['degree', 'maintenance']

        intersection_recommend_set = set()
        union_recommend_set = set()
        recommend_res = []
        recommend_files: List[Dict[str, Any]] = []
        for item in features:
            recommend_list = []
            if item == 'degree':
                recommend_list = cls.handle_get_degree(project_name, default_rate, rank_rates)
                recommend_files.append({'DegreeCentrality': recommend_list})
            elif item == 'drh':
                recommend_list = cls.handle_get_drh('tt')
                recommend_files.append({'DesignRuleHierarchy': recommend_list})
            elif item == 'maintenance':
                recommend_list = cls.handle_get_maintenance(src_dir, default_rate, rank_rates)
                recommend_files.append({'MaintenanceCost': recommend_list})
            recommend_res.append(set(recommend_list))
            union_recommend_set.update(recommend_list)
        if len(recommend_res) > 0:
            intersection_recommend_set = recommend_res[0]
        else:
            return
        for i in range(1, len(recommend_res)):
            intersection_recommend_set = intersection_recommend_set.intersection(recommend_res[i])

        # if mode == 'intersection':
        #     recommend_result = intersection_recommend_set
        #     print("intersection of recommended file: ")
        # else:
        #     recommend_result = union_recommend_set
        #     print("union of recommended file: ")
        # recommend_files = []
        # for file in recommend_result:
        #     recommend_files.append(str(file))
        recommend_files.append({'Union': list(union_recommend_set)})
        recommend_files.append({'Intersection': list(intersection_recommend_set)})
        return recommend_files

    @classmethod
    def handle_get_degree(cls, project_name: str, default_rate, rank_rates) -> List[str]:
        dep_path = cls.output_path + project_name + '/' + project_name + '-out/' + project_name + cls.dep_tail
        rate = default_rate if len(rank_rates) == 0 else rank_rates[0]
        recommend_degree = recommend_by_degree(rate, dep_path, project_name)
        return recommend_degree

    @classmethod
    def handle_get_drh(cls, drh_method) -> List[Path]:
        recommend_drh = recommend_by_drh(drh_method[0])
        return recommend_drh

    @classmethod
    def handle_get_maintenance(cls, src_dir: Path, default_rate, rank_rates, sort_by: str = None) -> List[str]:
        rate = default_rate if len(rank_rates) == 0 else rank_rates[1]
        if sort_by is not None:
            recommend_mc = recommend_by_maintenance(src_dir, rate, sort_by)
        else:
            recommend_mc = recommend_by_maintenance(src_dir, rate)
        return recommend_mc
