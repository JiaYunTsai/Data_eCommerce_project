import pandas as pd


class EachMemberItem:
    def __init__(self,behavior_member):
        self.member = behavior_member
        self.score = {'viewproduct':1,'search':2,'add':3,'checkout':4,'purchase':5}
        self.member['score'] = self.member['Behavior'].map(self.score)
        self.member_item_dict = {}
        
    def item_dict(self):
        self.member['score'].fillna(0,inplace=True)
        item = set(self.member['SalePageId'].to_list())
        member_item_dict = {}
        for i in item:
            member_item_dict[i] = self.member.loc[self.member['SalePageId'] == i,'score'].sum()
        self.member_item_dict = member_item_dict
        

class UserItem:
    def __init__(self,data):
        self.behaviordata = pd.read_excel(data)
        self.allmember = set(self.behaviordata['ShopMemberId'].to_list())
        self.memberitem_matrix ={}
        self.allitem = set(self.behaviordata['SalePageId'].to_list())
        self.nummatrix = None
        
    def user_item_dict(self):   
        allmember = self.allmember
        behaviordata = self.behaviordata
        memberitem_matrix ={}
        for i in allmember:
            memberdata = behaviordata.loc[behaviordata['ShopMemberId'] == i]
            memberitem = EachMemberItem(memberdata)
            memberitem.item_dict()
            memberitem_matrix[i]=memberitem.member_item_dict
        self.memberitem_matrix = memberitem_matrix
    def martix(self):
        allitem = list(self.allitem)
        allmember = list(self.allmember)
        memberitem_matrix = self.memberitem_matrix
        last_matrix = pd.DataFrame(columns=allitem,index=allmember)
        for i in allmember:
            for j in allitem:
                if memberitem_matrix[i].get(j) == None:
                    last_matrix.loc[i,j] = 0
                else:
                    last_matrix.loc[i,j] = memberitem_matrix[i].get(j)
        
        last_matrix.to_excel('./data/last_martix.xlsx')
        self.nummatrix= last_matrix.values
        

if __name__ == '__main__':
    usermatrix = UserItem('./data/testid_31.xlsx')
    usermatrix.user_item_dict()
    usermatrix.martix()
    print(usermatrix.nummatrix)