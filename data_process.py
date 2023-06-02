import pandas as pd

pd.options.mode.chained_assignment = None


class EachMemberItem:
    def __init__(self, behavior_member):
        self.member = behavior_member
        self.score = {
            "viewproduct": 1,
            "add": 3,
            "checkout": 4,
            "purchase": 0,
        }
        self.member.loc[:, "score"] = self.member["Behavior"].map(self.score).copy()
        self.member_item_dict = {}
        self.member_buy_dict = {}

    def item_dict(self):
        self.member["score"].fillna(0, inplace=True)
        item = set(self.member["SalePageId"].to_list())
        member_item_dict = {}
        for i in item:
            member_item_dict[i] = self.member.loc[
                self.member["SalePageId"] == i, "score"
            ].sum()
        self.member_item_dict = member_item_dict

    def buy_dict(self):
        purchase = self.member.loc[
            self.member["Behavior"] == "purchase", "SalePageId"
        ].to_list()
        member_buy_dict = {}
        for i in purchase:
            member_buy_dict[i] = 1
        self.member_buy_dict = member_buy_dict


def load_data(data):
    behaviordata = pd.read_excel(data)
    behaviordata["ShopMemberId"] = pd.factorize(behaviordata["ShopMemberId"])[0]
    allmember = set(behaviordata["ShopMemberId"].to_list())

    memberitem_matrix = {}
    memberbuy_matrix = {}

    for i in allmember:
        memberdata = behaviordata.loc[behaviordata["ShopMemberId"] == i]
        memberitem = EachMemberItem(memberdata)
        memberitem.item_dict()
        memberitem.buy_dict()
        memberitem_matrix[i] = memberitem.member_item_dict
        memberbuy_matrix[i] = memberitem.member_buy_dict

    allitem = set(behaviordata["SalePageId"].to_list())

    last_matrix = pd.DataFrame(columns=allitem, index=allmember)
    buy_yes_matrix = pd.DataFrame(columns=allitem, index=allmember)

    for i in allmember:
        for j in allitem:
            if memberitem_matrix[i].get(j) == None:
                last_matrix.loc[i, j] = 0
            else:
                last_matrix.loc[i, j] = memberitem_matrix[i].get(j)
            if buy_matrix[i].get(j) == None:
                buy_yes_matrix.loc[i, j] = 0
            else:
                buy_yes_matrix.loc[i, j] = buy_matrix[i].get(j)

    last_matrix.index.name = "userId"
    buy_yes_matrix.index.name = "userId"

    nummatrix = last_matrix.values
    buynummatrix = buy_yes_matrix

    return nummatrix, last_matrix, buynummatrix
