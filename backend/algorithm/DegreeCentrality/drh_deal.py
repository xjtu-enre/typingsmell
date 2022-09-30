import csv
import json


class drh:
    def __init__(self, file_name, Layer, Module):
        self.file_name = file_name
        self.Layer = Layer
        self.Module = Module


def drh_deal(file_url, file_list):
    with open(file_url, 'r') as f:
        file = json.loads(f.read())
        for type in file['structure']:
            Layer = type['name']
            if type['name'] != "Isolated":
                for cell in type['nested']:
                    Module = cell['name'].split('/')[1]
                    get_file(cell, Layer, Module, file_list)
            else:
                for isolated_file in type['nested']:
                    print(isolated_file)
                    file_list.append(drh(isolated_file['name'], "Isolated", "/"))


def get_file(cells, Layer, Module, file_list):
    if cells['@type'] == 'group':
        for cell in cells['nested']:
            get_file(cell, Layer, Module, file_list)
    if cells['@type'] == 'item':
        filenow = drh(cells['name'], Layer, Module)
        file_list.append(filenow)


def drh_statistical(file_url, out_url):
    file_list = []
    drh_deal(file_url, file_list)

    f = open(out_url, 'w', encoding='utf-8', newline="")
    csv_writer = csv.writer(f)
    csv_writer.writerow(["file", "Layer", "Module"])
    for file in file_list:
        csv_writer.writerow([file.file_name, file.Layer, file.Module])
    f.close()

# drh_statistical("C:/Users/ding7/Desktop/result-0325/numpy/out/numpy-result-drh.json",
#                 "C:/Users/ding7/Desktop/result-0325/numpy/out/numpy-result-drh.csv")
