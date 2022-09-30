# -*- coding: utf-8 -*-
from pathlib import Path
from xml.dom.minidom import parse
from collections import defaultdict, OrderedDict
import json

"""
Read the contents of the XML file and re-number the files in the project
Output a json file
"""


def has_element_child(nodename):
    has_element_child = 0
    for child in nodename.childNodes:
        if child.nodeType == 1:
            has_element_child += 1
    return has_element_child


def to_cell(src, dest, values, values_sum):
    value_note = defaultdict(list)

    for value in values:
        value = value.strip()
        value_note[value] = 1.0
    cell = {
        'src': src,
        'dest': dest,
        'values': value_note,
    }
    values_sum.append(cell)
    return values_sum


def readXML(url):
    domTree = parse(url)
    rootNode = domTree.documentElement
    print(rootNode.nodeName)

    file_node = dict()

    nodeid = rootNode.getElementsByTagName("node")
    for node in nodeid:
        id = node.getAttribute("id")
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE and has_element_child(
                    child) == 0:  # 当node为element类型,且无element类型的子节点时
                if child.getAttribute('name') == "longName":
                    # print(child.getAttribute("value"))
                    print(child.getAttribute("value").replace("\\", "/"))
                    file_node[id] = child.getAttribute("value").replace("\\", "/")

    print(file_node)
    print(len(file_node))
    change_file_id = dict()
    count = 0
    varibles = list()
    for key in file_node.keys():
        change_file_id[file_node[key]] = count
        count = count + 1
        varibles.append(file_node[key])
    print(change_file_id)

    edge_set = rootNode.getElementsByTagName("edge")
    values_sum = list()
    for edge in edge_set:
        src = edge.getAttribute("source")
        dest = edge.getAttribute("target")

        final_src = change_file_id[file_node[src]]
        final_dest = change_file_id[file_node[dest]]

        for child in edge.childNodes:
            if child.nodeType == child.ELEMENT_NODE and has_element_child(
                    child) == 0:  # 当node为element类型,且无element类型的子节点时
                if child.getAttribute('name') == "dependency kind":
                    print(child.getAttribute("value"))
                    depends = child.getAttribute("value").split(",")
                    values_sum = to_cell(final_src, final_dest, depends, values_sum)
    return varibles, values_sum


def write_to_json(varibles, values, filepath):
    test_dict = {
        '"@schemaVersion"': "1.0",
        'variables': varibles,
        'cells': values,
    }

    json_str = json.dumps(test_dict, indent=4)
    with open(filepath, 'w') as json_file:
        json_file.write(json_str)


def xml_to_json(xml_path, out_path, src_root: Path):
    varibles, values = readXML(xml_path)

    write_to_json(varibles, values, out_path)


if __name__ == '__main__':
    url = "C:/Users/ding7/Desktop/docutils_FileDependencyCytoscape.xml"
    filepath = "C:/Users/ding7/Desktop/network_deal/network_deal/test_data.json"
    xml_to_json(url, filepath)
