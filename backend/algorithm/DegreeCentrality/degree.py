import csv
import json
import os

import pandas as pd
import networkx as nx

'''
code logic:
input: enre result, understand result, file type
output: degree for each file, statistics for project, both are csv file
1, merge ENRE result and understand result 
-> Note that the result of Understand needs to be a relative path
-> output: projectname.json
2, create graph: use projectname.json
3, collect graph information
4, get degree information and statistic the proportion of each distribution
5, the output
'''


def create_graph(url):
    G = nx.DiGraph()
    with open(url, 'r') as f:
        file = json.loads(f.read())
        cells = file['cells']
        variables = file['variables']  # Get the filename for the node
        edge_list = set()
        for node in range(0, len(variables)):
            G.add_node(node)
        for cell in cells:
            G.add_edge(cell['src'], cell['dest'])
            edge_list.add((cell['src'], cell['dest']))
    return G, variables, edge_list


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


def count_deal(left, right, variable, diction, count_temp, count_temp_types, hastyped):
    for i in range(left, right):
        count_temp.append(variable[i])

        if diction[variable[i].replace('F:/analyze-projects/matplotlib-3.3/matplotlib-3.3.3/lib/', '')] == 'typed':
            count_temp_types.append(variable[i])

    return "%.2f%%" % ((len(count_temp_types) / len(count_temp)) * 100), "%.2f%%" % (
            (len(count_temp_types) / len(hastyped)) * 100)


def count_by_step(variable, diction, hastyped):
    step = int(len(variable) / 10)
    length = []
    for i in range(10):
        length.append(int(step * i))
    length.append(len(variable))
    count_temp = []
    count_temp_types = []
    temp_ratio = []
    typed_ratio = []
    for i in range(10):
        left = length[i]
        right = length[i + 1]
        print(left, right)
        temp, typed = count_deal(left, right, variable, diction, count_temp, count_temp_types, hastyped)
        temp_ratio.append(temp)
        typed_ratio.append(typed)
    return temp_ratio, typed_ratio


def degree_statistical(result, variables, typed, dictionary):
    variable_temp = variables
    quick_sort(result, variable_temp, 0, len(result) - 1)
    temp_ratio, typed_ratio = count_by_step(variable_temp, dictionary, typed)
    list = sorted(result.items(), key=lambda d: d[0])
    return [item[1] for item in list], temp_ratio, typed_ratio


def typed_deal(filepath):
    data = pd.read_csv(filepath)
    dictionary = {}
    type = data['file type']
    for line in data:
        if line == 'file path':
            name = data[line]
            for i in range(len(name)):
                dictionary[name[i].replace("\\", "/")] = type[i]
    typed = []
    for key in dictionary.keys():
        if (dictionary[key] == 'typed'):
            typed.append(dictionary[key])
    return typed, dictionary


def degree_processing(G, variables, typed_url, node_url, statistic_url):
    typed, dictionary = typed_deal(typed_url)
    node_result = range(0, G.number_of_nodes())
    degree_centrality, degree_temp_ratio, degree_typed_ratio = degree_statistical(nx.degree_centrality(G), variables,
                                                                                  typed, dictionary)

    node_columns = ["NodeID", "Nodename", "degree_centrality"]
    with open(node_url, 'w', newline='') as t_file:
        csv_writer = csv.writer(t_file)
        csv_writer.writerow(node_columns)
        for l in range(len(node_result)):
            csv_writer.writerow([node_result[l], variables[l], '%.4f' % degree_centrality[l]])
    index = []
    for i in range(1, 11):
        index.append("Top %d" % (i * 10) + "%")
    data = {"measurement": index, "degree_precision": degree_temp_ratio,
            "degree_recall": degree_typed_ratio}
    df = pd.DataFrame(data)
    df.to_csv(statistic_url, mode='a', index=False)


def get_degree(dependency_url, typed_url, degree_url, statistic_url):
    # input
    # dependency_url = ""
    # typed_url = ""

    # output
    # degree_url = ""
    # statistic_url = ""

    G, variables, edge_list = create_graph(dependency_url)
    degree_processing(G, variables, typed_url, degree_url, statistic_url)
