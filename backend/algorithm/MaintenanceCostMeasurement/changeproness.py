import csv


def readNodeDict(fileName):
    nodeDict = dict()
    with open(fileName, "r", encoding='utf-8') as fp:
        reader = csv.reader(fp, delimiter=",")
        for each in reader:
            if each[0] == 'id':
                continue
            id = each[0]
            name = each[1]
            nodeDict[id] = name
    return nodeDict


def read_dep_file(node_file):
    resList = list()
    nodeDict = readNodeDict(node_file)
    #nodeTypeDict = readEdgeDict(edge_file)
    for id in nodeDict.keys():
        name = nodeDict[id]
        tmp = [id, name]
        resList.append(tmp)
    return resList


def formatFileName(fileNameList):
    for index in range(0, len(fileNameList)):
        fileName = fileNameList[index]
        # fileName = fileName.replace(".", "_")
        fileName = fileName.replace("/", "\\")
        fileNameList[index] = fileName
    return fileNameList


#read mc file
def read_mc_file(mc_file):
    mcAuthorDict = dict()   # [filename][author] = the commit count by this author
    mcCommittimesDict = dict() #[filename] = cmttimes
    mcChangeLocDict = dict()  #[fileName] = loc
    mcIssueCountDict = dict()  #[fileName][issueId] = issue cmt counts
    mcIssueLocDict = dict()  #[fileName][issueId] = issueloc
    with open(mc_file, "r", encoding="utf8") as fp:
        reader = csv.reader(fp, delimiter=",")
        for each in reader:
            [commitId, author, date, issueIds, files, addLocs, delLocs] = each
            fileNameList = files.split(";")
            addLocList = addLocs.split(";")
            delLocList = delLocs.split(";")
            if issueIds == "":
                issueIdList=list()
            else:
                issueIdList = issueIds.split(";")

            # print(fileNameList)
            fileNameLsist = formatFileName(fileNameList)
            # print(fileNameList)

            #author releated
            for fileName in fileNameList:
                if fileName not in mcAuthorDict:
                    mcAuthorDict[fileName] = dict()
                if author not in mcAuthorDict[fileName]:
                    mcAuthorDict[fileName][author] = 1
                else:
                    mcAuthorDict[fileName][author] += 1

            # commit times related
            for fileName in fileNameList:
                if fileName not in mcCommittimesDict:
                    mcCommittimesDict[fileName] = 1
                else:
                    mcCommittimesDict[fileName] += 1

            # LOC changed related
            for index in range(0, len(fileNameList)):
                fileName = fileNameList[index]
                loc = int(addLocList[index]) + int(delLocList[index])
                if fileName not in mcChangeLocDict:
                    mcChangeLocDict[fileName] = loc
                else:
                    mcChangeLocDict[fileName] += loc

            #issue counts related
            for index in range(0, len(fileNameList)):
                fileName = fileNameList[index]
                if fileName not in mcIssueCountDict:
                    mcIssueCountDict[fileName] = dict()
                for issueId in issueIdList:
                    if issueId not in mcIssueCountDict[fileName]:
                        mcIssueCountDict[fileName][issueId] = 1
                    else:
                        mcIssueCountDict[fileName][issueId] += 1

            #issue loc related
            for index in range(0, len(fileNameList)):
                fileName = fileNameList[index]
                loc = int(addLocList[index]) + int(delLocList[index])
                if fileName not in mcIssueLocDict:
                    mcIssueLocDict[fileName] = dict()
                for issueId in issueIdList:
                    if issueId not in mcIssueLocDict[fileName]:
                        mcIssueLocDict[fileName][issueId] = loc
                    else:
                        mcIssueLocDict[fileName][issueId] += loc
    return mcAuthorDict, mcCommittimesDict, mcChangeLocDict, mcIssueCountDict, mcIssueLocDict


def search_author_count(mcAuthorDict, fileName):
    if fileName in mcAuthorDict:
        return len(list(mcAuthorDict[fileName].keys()))
    else:
        return 0


def search_count(aDict, fileName):
    if fileName in aDict:
        return aDict[fileName]
    else:
        return 0


def search_issue_count(mcIssueCountDict, fileName):
    issueCount = 0
    if fileName in mcIssueCountDict:
        issueCount = len(list(mcIssueCountDict[fileName].keys()))
        issueCmtCount = sum(list(mcIssueCountDict[fileName].values()))
    else:
        issueCount = 0
        issueCmtCount = 0
    return issueCount, issueCmtCount


def search_iisue_loc(mcIssueLocDict, fileName):
    if fileName in mcIssueLocDict:
        loc = sum(list(mcIssueLocDict[fileName].values()))
        return loc
    else:
        return 0


def change_bug_proness_compute(fileName_deptype_list, mcAuthorDict, mcCommittimesDict, mcChangeLocDict, mcIssueCountDict, mcIssueLocDict):
    for index in range(0, len(fileName_deptype_list)):
        each = fileName_deptype_list[index]
        fileName = each[1]
        authorCount = search_author_count(mcAuthorDict, fileName)
        cmtCount = search_count(mcCommittimesDict, fileName)
        changeLoc = search_count(mcChangeLocDict, fileName)
        [issueCount, issueCmtCount] = search_issue_count(mcIssueCountDict, fileName)
        issueLoc = search_iisue_loc(mcIssueLocDict, fileName)
        fileName_deptype_list[index].append(authorCount)
        fileName_deptype_list[index].append(cmtCount)
        fileName_deptype_list[index].append(changeLoc)
        fileName_deptype_list[index].append(issueCount)
        fileName_deptype_list[index].append(issueCmtCount)
        fileName_deptype_list[index].append(issueLoc)
        # print(fileName_deptype_list[index])
    return fileName_deptype_list


def writeCSV(aList, fileName):
    with open(fileName, "w", newline="", encoding='utf-8') as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(aList)
    # print(fileName)

def changeproness(node_file, mc_file, outfile):
    fileName_deptype_list = read_dep_file(node_file)
    [mcAuthorDict, mcCommittimesDict, mcChangeLocDict, mcIssueCountDict, mcIssueLocDict] = read_mc_file(mc_file)
    change_bug_cost_list = change_bug_proness_compute(fileName_deptype_list, mcAuthorDict, mcCommittimesDict, mcChangeLocDict, mcIssueCountDict, mcIssueLocDict)
    title = ['id', 'filename', '#author', '#cmt', 'changeloc', '#issue', '#issue-cmt', 'issueLoc']
    final = list()
    final.append(title)
    final.extend(change_bug_cost_list)
    writeCSV(final, outfile)


