
class ModifyDetail:
    def __init__(self, fileList, addList, delList):
        self.fileList = fileList #[f1, f2]
        self.addList = addList   #[loc, loc]
        self.delList = delList   #[loc, loc]

    def toList(self):
        aList = list()
        aList.append(toStrFromList(self.fileList))
        aList.append(toStrFromList(self.addList))
        aList.append(toStrFromList(self.delList))
        return aList


class CommitDetail:
    def __init__(self, commitId, author, date, issueIds, modifyDetail):
        self.commitId = commitId
        self.author = author  #name not email
        self.date = date
        self.issueIds = issueIds
        self.modifyDetail = modifyDetail

    def toList(self):
        aList = list()
        aList.append(self.commitId)
        aList.append(self.author)
        aList.append(self.date)
        aList.append(toStrFromList(self.issueIds))
        aList.extend(self.modifyDetail.toList())
        return aList

def toStrFromList(aList):
    stralist = list()
    for each in aList:
        stralist.append(str(each))
    return ";".join(stralist)
