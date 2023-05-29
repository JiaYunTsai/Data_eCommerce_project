import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
pd.options.mode.chained_assignment = None


class EachMemberItem:
    def __init__(self, behavior_member):
        self.member = behavior_member
        self.score = {'viewproduct': 1, 'search': 2,
                      'add': 3, 'checkout': 4, 'purchase': 5}
        self.member.loc[:, 'score'] = self.member['Behavior'].map(
            self.score).copy()
        self.member_item_dict = {}

    def item_dict(self):
        self.member['score'].fillna(0, inplace=True)
        item = set(self.member['SalePageId'].to_list())
        member_item_dict = {}
        for i in item:
            member_item_dict[i] = self.member.loc[self.member['SalePageId']
                                                  == i, 'score'].sum()
        self.member_item_dict = member_item_dict
        # return member_item_dict


class UserItem:
    def __init__(self, data):
        self.behaviordata = pd.read_excel(data)
        # 因應推薦序桶排序時需要使用數字
        self.behaviordata['ShopMemberId'] = pd.factorize(
            self.behaviordata['ShopMemberId'])[0]
        self.allmember = set(self.behaviordata['ShopMemberId'].to_list())
        self.memberitem_matrix = {}
        self.allitem = set(self.behaviordata['SalePageId'].to_list())
        self.nummatrix = None
        self.last_matrix = None

    def user_item_dict(self):
        allmember = self.allmember
        behaviordata = self.behaviordata
        memberitem_matrix = {}
        for i in allmember:
            memberdata = behaviordata.loc[behaviordata['ShopMemberId'] == i]
            memberitem = EachMemberItem(memberdata)
            memberitem.item_dict()
            memberitem_matrix[i] = memberitem.member_item_dict
        self.memberitem_matrix = memberitem_matrix

    def martix(self):
        allitem = list(self.allitem)
        allmember = list(self.allmember)
        memberitem_matrix = self.memberitem_matrix
        last_matrix = pd.DataFrame(columns=allitem, index=allmember)
        for i in allmember:
            for j in allitem:
                if memberitem_matrix[i].get(j) == None:
                    last_matrix.loc[i, j] = 0
                else:
                    last_matrix.loc[i, j] = memberitem_matrix[i].get(j)
        last_matrix.index.name = 'userId'
        last_matrix.to_excel('last_martix.xlsx')
        self.nummatrix = last_matrix.values
        self.last_matrix = last_matrix


def recommend_products(user_id, user_similarity, user_item_matrix):
    unrated_products = user_item_matrix.loc[user_id, :].isna()
    unrated_products = unrated_products.index.values
    k = 3
    similar_users = user_similarity[user_id].argsort()[-k:][::-1]
    similar_user_ratings = user_item_matrix.loc[similar_users,
                                                unrated_products]
    # Calculate the weighted average of the ratings.
    recommended_ratings = similar_user_ratings.mean(axis=0)
    # Sort the recommended ratings by descending order.
    recommended_ratings = np.array(recommended_ratings).argsort()[::-1]
    # Return the top-k recommended products.
    return unrated_products[recommended_ratings[:k]]


"""
usermatrix.nummatrix 評分矩陣

usermatrix.last_matrix 評分的DF

"""
#

if __name__ == '__main__':
    usermatrix = UserItem(
        '/Users/aston/Downloads/91APP_DataSet_2023/BehaviorData/Data_eCommerce_project/testid_2_num.xlsx')
    usermatrix.user_item_dict()
    usermatrix.martix()
    # print(usermatrix.last_matrix)
    # print(usermatrix.nummatrix)

    user_similarity = cosine_similarity(usermatrix.nummatrix)
    item_sim_matrix = np.dot(usermatrix.nummatrix.T, usermatrix.nummatrix)

    recommend_result = recommend_products(
        usermatrix.last_matrix.index[2], user_similarity, usermatrix.last_matrix)
    print(recommend_result)
