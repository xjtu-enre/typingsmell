from typing import List, Dict


class TypingTrans:
    @classmethod
    def dict_to_list(cls, lis: List, dic: Dict):
        temp_dic = dic.copy()
        trans_list = []
        for item in lis:
            try:
                trans_item = temp_dic[item]
                del temp_dic[item]
            except:
                trans_item = 0
            trans_list.append(trans_item)
        return trans_list, temp_dic
