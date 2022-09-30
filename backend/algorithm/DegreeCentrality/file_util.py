import json

"""
merge explicit dependency and possible dependency file
    First adjust the index of the file
    Next merge
"""


def read_json(url, from_file_name):
    from_file_name_id = -1
    to_file = set()
    with open(url, 'r') as f:
        file = json.loads(f.read())
        cells = file['cells']
        variables = file['variables']  # Get the filename for the node
        for id in range(len(variables)):
            if (variables[id]) == from_file_name:
                from_file_name_id = id
        if from_file_name_id == -1:
            return
        for cell in cells:
            if cell['src'] == from_file_name_id:
                to_file.add(variables[cell['dest']])

    return to_file


def test_file_number(url1, url2, prefixion):
    set_possible = set()
    set_explicit = set()
    with open(url1, 'r') as f:
        file1 = json.loads(f.read())
        for variable in file1['variables']:
            set_possible.add(variable.replace(prefixion, ""))
    with open(url2, 'r') as f:
        file2 = json.loads(f.read())
        for variable in file2['variables']:
            set_explicit.add(variable)


def write_to_json(variables, values, projectname, filepath):
    test_dict = {
        '"@schemaVersion"': "1.0",
        'name': projectname,
        'variables': variables,
        'cells': values,
    }

    json_str = json.dumps(test_dict, indent=4)
    with open(filepath, 'w') as json_file:
        json_file.write(json_str)


def merge(url1, url2, filepath, prefixion=""):
    file_id = dict()
    with open(url1, 'r') as f:
        file1 = json.loads(f.read())
        variables1 = file1['variables']
        cells = file1['cells']
        for id in range(len(variables1)):
            file_id[variables1[id].replace(prefixion, "")] = id
            variables1[id] = variables1[id].replace(prefixion, "")
        print(file_id)

    with open(url2, 'r') as f:
        file2 = json.loads(f.read())
        variables2 = file2['variables']
        cell_for_possible_dep = file2['cells']
        print(cell_for_possible_dep)
        for cell_record in cell_for_possible_dep:
            cell_record['src'] = file_id[variables2[(cell_record['src'])]]
            cell_record['dest'] = file_id[variables2[(cell_record['dest'])]]
        print(cell_for_possible_dep)
    cells = cells + cell_for_possible_dep
    write_to_json(variables1, cells, "returns", filepath)





