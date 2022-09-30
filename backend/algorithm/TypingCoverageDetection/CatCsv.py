import os
import sys
import csv
from pathlib import Path
from typing import List

from algorithm.TypingCoverageDetection.CsvItem import to_csvItem, cat_csv_item

csv_list: List[Path] = []


def cat_csvs():
    argv = sys.argv[1:]
    for raw_path in argv:
        if raw_path == "-o":
            break
        path = Path(raw_path)
        walk_tree(path)
    new_csv_items = []
    for csv_path in csv_list:
        with open(csv_path, "r", encoding="utf-8") as file:
            csv_head, *csv_items = csv.reader(file)
            for item in csv_items:
                new_csv_items.append(to_csvItem(csv_head, item))
    csv_content = cat_csv_item(new_csv_items)
    csv_name = "joined.csv"
    if argv[-2] == "-o":
        csv_name = argv[-1]
    with open(csv_name, "w", encoding="utf-8") as out_csv:
        out_csv.write(csv_content)


def walk_tree(path: Path):
    if path.is_dir():
        with os.scandir(path) as entries:
            for entry in entries:
                walk_tree(Path(entry))
    elif path.name.endswith(".csv"):
        csv_list.append(path)


if __name__ == '__main__':
    cat_csvs()
