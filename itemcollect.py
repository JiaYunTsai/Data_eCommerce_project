import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

pd.options.mode.chained_assignment = None


class EachMemberItem:
    def __init__(self, behavior_member):
        self.member = behavior_member
        self.score = {
            "viewproduct": 1,
            "search": 2,
            "add": 3,
            "checkout": 4,
            "purchase": 5,
        }
        self.member.loc[:, "score"] = self.member["Behavior"].map(self.score).copy()
        self.member_item_dict = {}

    def item_dict(self):
        self.member["score"].fillna(0, inplace=True)
        item = set(self.member["SalePageId"].to_list())
        member_item_dict = {}
        for i in item:
            member_item_dict[i] = self.member.loc[
                self.member["SalePageId"] == i, "score"
            ].sum()
        self.member_item_dict = member_item_dict
        # return member_item_dict


class UserItem:
    def __init__(self, data):
        self.behaviordata = pd.read_excel(data)
        # 因應推薦序桶排序時需要使用數字
        self.behaviordata["ShopMemberId"] = pd.factorize(
            self.behaviordata["ShopMemberId"]
        )[0]
        self.allmember = set(self.behaviordata["ShopMemberId"].to_list())
        self.memberitem_matrix = {}
        self.allitem = set(self.behaviordata["SalePageId"].to_list())
        self.nummatrix = None
        self.last_matrix = None

    def user_item_dict(self):
        allmember = self.allmember
        behaviordata = self.behaviordata
        memberitem_matrix = {}
        for i in allmember:
            memberdata = behaviordata.loc[behaviordata["ShopMemberId"] == i]
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
        last_matrix.index.name = "userId"
        last_matrix.to_excel("last_martix.xlsx")
        self.nummatrix = last_matrix.values
        self.last_matrix = last_matrix


class recommend_system:
    def recommend_similarity(user_id, user_similarity, user_item_matrix):
        unrated_products = user_item_matrix.loc[user_id, :].isna()
        unrated_products = unrated_products.index.values
        k = 3  # 找k位最相似的
        similar_users = user_similarity[user_id].argsort()[-k:][::-1]
        similar_user_ratings = user_item_matrix.loc[similar_users, unrated_products]
        recommended_ratings = similar_user_ratings.mean(axis=0)
        recommended_ratings = np.array(recommended_ratings).argsort()[::-1]
        return unrated_products[recommended_ratings[:k]]

    def recommend_content(user_id, user_item_matrix):
        unrated_products_index = pd.Index(pd.isna(user_item_matrix[user_id]))

        # Predict the ratings for the unrated products.
        predicted_ratings = user_item_matrix.dot(
            svd.inverse_transform(user_item_matrix[user_id])
        )

        # Sort the predicted ratings by descending order.
        predicted_ratings = np.array(predicted_ratings).argsort()[::-1]

        # Return the top-k recommended products.
        return user_item_matrix.columns[unrated_products_index][predicted_ratings[:5]]

    def generate_recommendations(user_id, top_n):
        user_item_matrix = usermatrix.last_matrix
        user_ratings = user_item_matrix.loc[user_id]
        user_predictions = item_sim_matrix.dot(user_ratings)
        recommended_indices = user_predictions.argsort()[-top_n:][::-1]
        recommended_products = user_item_matrix.columns[recommended_indices]
        return recommended_products


##寫一個 user_item_matrix
"""
usermatrix.nummatrix 評分矩陣

usermatrix.last_matrix 評分的DF

"""
#


if __name__ == "__main__":
    usermatrix = UserItem(
        "/Users/aston/Downloads/91APP_DataSet_2023/BehaviorData/Data_eCommerce_project/testid_2_num.xlsx"
    )
    usermatrix.user_item_dict()
    usermatrix.martix()
    # print(usermatrix.last_matrix)
    # print(usermatrix.nummatrix)

    user_similarity = cosine_similarity(usermatrix.nummatrix)
    item_sim_matrix = np.dot(usermatrix.nummatrix.T, usermatrix.nummatrix)

    recommend_result = recommend_system.recommend_similarity(
        usermatrix.last_matrix.index[2], user_similarity, usermatrix.last_matrix
    )
    # print(recommend_result)
    usermatrix.last_matrix.columns = usermatrix.last_matrix.columns.astype(str)
    # print(type(usermatrix.last_matrix.columns[0]))
    # print(type(usermatrix.last_matrix))
    svd = TruncatedSVD(n_components=100)
    user_item_matrix_svd = svd.fit_transform(usermatrix.last_matrix)
    recommended_products = user_item_matrix_svd[
        usermatrix.last_matrix.index[2]
    ].argsort()[::-1][:4]
    user_id = usermatrix.last_matrix.index[2]
    recommendations = recommend_system.generate_recommendations(user_id, 3)
    # print(pd.DataFrame(user_item_matrix_svd))
    print(recommended_products)
    # print(recommendations)
    print(f"Top 3 Recommendations for User {user_id}: {recommendations}")
