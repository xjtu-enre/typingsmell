from collections import defaultdict
from typing import List, Dict, Union


class CsvItem:
    def __init__(self, map: Dict[str, Union[int, str]]):
        self.map: Dict[Union[int, str]] = defaultdict(int, map)

    def __str__(self) -> str:
        res = ""
        for key, value in self.map.items():
            res += f"{key}: {value},"
        return res[:-1] if res != "" else ""

    def __getitem__(self, key):
        return self.map[key]

    def __setitem__(self, key, value):
        self.map[key] = value


    def gen_csv_header(self) -> str:
        header = ""
        for key, value in self.map.items():
            header += key + ","
        header = header[:-1] + "\n"
        return header

    def gen_csv_line(self) -> str:
        line = ""
        for key, value in self.map.items():
            line += str(value) + ","
        line = line[:-1] + "\n"
        return line


def union_csv_items(*args: CsvItem) -> str:
    head = line = "\n"
    for item in args:
        head = f"{head[:-1]},{item.gen_csv_header()}"
        line = f"{line[:-1]},{item.gen_csv_line()}"
    head = head[1:]
    line = line[1:]
    return head + line


def union_csv_items_1(*args: CsvItem) -> CsvItem:
    res = CsvItem({})
    for item in args:
        for key, value in item.map.items():
            res.map[key] = value
    return res


def cat_csv_item(items: List[CsvItem]) -> str:
    heads = collect_heads(items)
    res = ""
    for head in heads:
        res += head + ","
    res = res[:-1] + "\n"
    for item in items:
        for head in heads:
            res += str(item[head]) + ","
        res = res[:-1] + "\n"
    return res


def collect_heads(items: List[CsvItem]) -> List[str]:
    res = []
    for item in items:
        for head, _ in item.map.items():
            res.append(head)
    return list(dict.fromkeys(res))


def to_csvItem(heads: List[str], terms: List[str]) -> CsvItem:
    tempDict = {}
    for head, term in zip(heads, terms):
        tempDict[head] = term
    return CsvItem(tempDict)
