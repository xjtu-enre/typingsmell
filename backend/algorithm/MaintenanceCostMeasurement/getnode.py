import os
import csv


def writeCSV(aList, fileName):
    with open(fileName, "w", newline="", encoding='utf-8') as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(aList)


def get_nodefile(dir, out_url):
    fileList_all = set()
    for filename, dirs, files in os.walk(dir, topdown=True):
        # filename = filename.replace("\\", "/")
        filename = filename.split(dir, 1)[1]
        if filename.startswith(".git") or filename.startswith(".github"):
            continue
        for file in files:
            file_temp = filename + "\\" + file
            file_temp = file_temp[1:]
            fileList_all.add(file_temp)
    count = 0
    result = list()
    result.append(['id', 'label'])
    for file in fileList_all:
        row = [count, file]
        result.append(row)
        count = count + 1
    writeCSV(result, out_url)
