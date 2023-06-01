import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


pd.options.mode.chained_assignment = None


class EachMemberItem:
    def __init__(self, behavior_member):
        self.member = behavior_member
        self.score = {
            "viewproduct": 1,
            "add": 3,
            "checkout": 4,
            "purchase": 5,
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


class UserItem:
    def __init__(self, data):
        self.behaviordata = pd.read_excel(data)
        self.RawuserID = [
            x
            for i, x in enumerate(self.behaviordata["ShopMemberId"].to_list())
            if x not in self.behaviordata["ShopMemberId"].to_list()[:i]
        ]
        # 因應推薦系統排序時需要使用數字
        self.behaviordata["ShopMemberId"] = pd.factorize(
            self.behaviordata["ShopMemberId"]
        )[0]
        self.allmember = set(self.behaviordata["ShopMemberId"].to_list())
        self.memberitem_matrix = {}
        self.allitem = set(self.behaviordata["SalePageId"].to_list())
        self.nummatrix = None
        self.last_matrix = None
        self.buynummatrix = None

    def user_item_dict(self):
        allmember = self.allmember
        behaviordata = self.behaviordata
        memberitem_matrix = {}
        memberbuy_matrix = {}
        for i in allmember:
            memberdata = behaviordata.loc[behaviordata["ShopMemberId"] == i]
            memberitem = EachMemberItem(memberdata)
            memberitem.item_dict()
            memberitem.buy_dict()
            memberitem_matrix[i] = memberitem.member_item_dict
            memberbuy_matrix[i] = memberitem.member_buy_dict
        self.memberitem_matrix = memberitem_matrix
        self.memberbuy_matrix = memberbuy_matrix

    def martix(self):
        allitem = list(self.allitem)
        allmember = list(self.allmember)
        memberitem_matrix = self.memberitem_matrix
        buy_matrix = self.memberbuy_matrix
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
        last_matrix.to_excel("last_martix.xlsx")
        buy_yes_matrix.index.name = "userId"
        buy_yes_matrix.to_excel("buy_yes_martix.xlsx")
        self.nummatrix = last_matrix.values
        self.last_matrix = last_matrix
        self.buynummatrix = buy_yes_matrix.values


class Recommend_system:
    def __init__(self):
        self.user_similarity = None

    def martix_to_similarity(self, nummatrix):
        self.user_similarity = cosine_similarity(nummatrix)

    def recommend_similarity(
        self, user_id, user_similarity, user_item_matrix, k
    ):  # 找k個最相似的
        unrated_products = user_item_matrix.loc[user_id, :].isna()  # 未瀏覽過
        # unrated_products = user_item_matrix.loc[user_id, :].isna() | (
        #     user_item_matrix.loc[user_id, :] < 10
        # )
        unrated_products = unrated_products.index.values  # 商品ID
        similar_users = user_similarity[user_id].argsort()[-k:][::-1]
        similar_user_ratings = user_item_matrix.loc[similar_users, unrated_products]
        recommended_ratings = similar_user_ratings.mean(axis=0)
        recommended_ratings = np.array(recommended_ratings).argsort()[::-1]
        return (
            similar_users.tolist(),
            unrated_products[recommended_ratings[:k]].tolist(),
        )

    def recommend_compareing(
        self, user_id, firstuser_of_recommendation, user_item_matrix, k
    ):
        unrated_products = user_item_matrix.loc[user_id, :].isna()  # 未瀏覽過
        # unrated_products = user_item_matrix.loc[user_id, :].isna() | (
        #     user_item_matrix.loc[user_id, :] < 10
        # )
        unrated_products = unrated_products.index.values  # 商品ID
        similar_user_ratings = user_item_matrix.loc[
            firstuser_of_recommendation, unrated_products
        ]
        recommended_ratings = similar_user_ratings.mean(axis=0)
        recommended_ratings = np.array(recommended_ratings).argsort()[::-1]
        return (unrated_products[recommended_ratings[:k]].tolist(),)


class ProductName:
    def __init__(self, dataset):
        self.dataset = pd.read_csv(dataset)
        self.salepage_dict = self.create_salepage_dict()

    def create_salepage_dict(self):
        salepage_dict = {}
        for index, row in self.dataset.iterrows():
            salepage_id = row["SalePage_Id"]
            salepage_title = row["SalePage_Title"]
            salepage_dict[salepage_id] = salepage_title

        return salepage_dict

    def get_salepage_title(self, salepage_id):
        return self.salepage_dict.get(salepage_id, "Title not found")


class ExecuteSystem:
    def __init__(self, behavior_data, salepage_data, number_of_product):
        self.user_matrix = UserItem(behavior_data)
        self.user_matrix.user_item_dict()
        self.user_matrix.martix()
        self.product_name = ProductName(salepage_data)
        self.rs = Recommend_system()
        self.k = number_of_product
        self.find_index = None

    def process_recommendation(self):
        self.rs.martix_to_similarity(self.user_matrix.nummatrix)
        recommendations = self.rs.recommend_similarity(
            self.user_matrix.last_matrix.index[0],
            self.rs.user_similarity,
            self.user_matrix.last_matrix,
            self.k,
        )
        print("推薦結果")
        for salepage_id, i in zip(
            recommendations[1], range(1, len(recommendations[1]) + 1)
        ):
            salepage_title = self.product_name.get_salepage_title(salepage_id)
            print(f"推薦第{i}名為：{salepage_title} ")

        all_user_Id = self.user_matrix.RawuserID
        user_of_recommendation = [all_user_Id[i] for i in recommendations[0]]
        print(f"Group ID:{user_of_recommendation}")

        return user_of_recommendation, recommendations[1]

    def process_recomm_comparing(self, first_of_user):
        self.find_index = [
            index
            for index, value in enumerate(self.user_matrix.RawuserID)
            if value in first_of_user
        ]
        # print(self.find_index)
        print("Group AA in the Second Time")
        recommendations_comparing = self.rs.recommend_compareing(
            self.user_matrix.last_matrix.index[0],
            self.find_index,
            self.user_matrix.last_matrix,
            self.k,
        )
        recommendations_comparing = recommendations_comparing[0]
        for salepage_id, i in zip(
            recommendations_comparing, range(1, len(recommendations_comparing) + 1)
        ):
            salepage_title = self.product_name.get_salepage_title(salepage_id)
            print(f"推薦第{i}名為：{salepage_title} ")
        return recommendations_comparing


if __name__ == "__main__":
    """
    k為決定推薦幾名
    """
    k = 5
    # 第一次
    print("Group AA")
    execute_system = ExecuteSystem("testid_31.xlsx", "SalePageData.csv", k)
    first_of_user = execute_system.process_recommendation()
    # 第二次
    print("Group BB")
    execute_system = ExecuteSystem("testid_31.xlsx", "SalePageData.csv", k)
    salepageid_of_BB = execute_system.process_recommendation()

    # 比較
    salepageid_of_AA = execute_system.process_recomm_comparing(first_of_user[0])
    print(salepageid_of_AA, "\n", salepageid_of_BB[1])
    correct_predictions = sum(
        1 for x, y in zip(salepageid_of_AA, salepageid_of_BB[1]) if x == y
    )
    accuracy = correct_predictions / len(salepageid_of_BB[1]) * 100
    print(f"準確率：{accuracy:.2f}%")
    fibd = UserItem("testid_31.xlsx")
    print(fibd.RawuserID, "\n", execute_system.RawuserId)
