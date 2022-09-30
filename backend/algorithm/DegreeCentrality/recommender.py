import csv
from pathlib import Path
from typing import List

import networkx as nx

from algorithm.DegreeCentrality.degree import create_graph, typed_deal, degree_statistical
from algorithm.MaintenanceCostMeasurement.changeproness import changeproness
from algorithm.MaintenanceCostMeasurement.getnode import get_nodefile
from algorithm.MaintenanceCostMeasurement.gitlogprocessor import gitlog


def process_degree(G, variables):
    nodes = []
    degree_centrality = nx.degree_centrality(G)
    for i in range(0, len(variables)):
        nodes.append((variables[i], degree_centrality[i]))

    nodes.sort(key=lambda line: line[1], reverse=True)
    return [Path(x[0]) for x in nodes]


def recommend_by_degree(rate: float, dependency_url, project_name) -> List[str]:
    G, variables, edge_list = create_graph(dependency_url)

    sorted_nodes = process_degree(G, variables)
    top_k_nodes = sorted_nodes[:int(rate * len(sorted_nodes))]
    return [str(var).replace("\\", '/').split('projects/' + project_name + '/')[1] for var in top_k_nodes]


def recommend_by_drh(drh_url) -> list:
    recommend_path = list()
    with open(drh_url, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[1] == 'L0':
                recommend_path.append(row[0])

    return recommend_path


def recommend_by_maintenance(src_dir: Path, rate: float, target='#author') -> List[str]:
    rootDir = str(src_dir.absolute().parent.parent).replace("\\", "/") + "/"
    project_path = rootDir + 'projects/'
    mc_path = rootDir + 'calculation/'
    project_name = src_dir.name
    gitlog(project_path, mc_path, project_name)
    dir = project_path + project_name
    mc_file = mc_path + project_name + '/mc/history-py.csv'
    outfile = mc_path + project_name + '/mc/file-mc.csv'
    node_url = mc_path + project_name + '/' + project_name + "-node.csv"
    get_nodefile(dir, node_url)
    changeproness(node_url, mc_file, outfile)
    maintenance_url = outfile
    target_data = list()
    variable = list()
    i = 0
    if target == '#author':
        i = 2
    elif target == '#cmt':
        i = 3
    elif target == 'changeloc':
        i = 4
    elif target == '#issue':
        i = 5
    elif target == '#issue-cmt':
        i = 6
    elif target == 'issueLoc':
        i = 7
    else:
        print("Wrong Input!")
        return []

    with open(maintenance_url, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            target_data.append(row[i])
            variable.append(row[1])
    if (len(target_data) * rate <= 0) | (rate > 1.0):
        print("Wrong Rate Input!")
        return []

    quick_sort(target_data, variable, 0, len(target_data) - 1)

    recommend_path = variable[0: (int)(len(target_data) * rate)]
    return [x.replace("\\", '/') for x in recommend_path]


def quick_sort(nums: list, variable: list, left: int, right: int) -> None:
    if left < right:
        i = left
        j = right
        pivot = nums[left]
        pivot_variable = variable[left]
        while i != j:
            while j > i and nums[j] < pivot:
                j -= 1
            if j > i:
                nums[i] = nums[j]
                variable[i] = variable[j]
                i += 1
            while i < j and nums[i] > pivot:
                i += 1
            if i < j:
                nums[j] = nums[i]
                variable[j] = variable[i]
                j -= 1
        nums[i] = pivot
        variable[i] = pivot_variable
        quick_sort(nums, variable, left, i - 1)
        quick_sort(nums, variable, i + 1, right)
