import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity


class Recommend_system:
    def __init__(self):
        self.user_similarity = None

    def martix_to_similarity(self, nummatrix):
        self.user_similarity = cosine_similarity(nummatrix)

    def recommend_similarity(
        self, user_id, user_similarity, user_item_matrix, k
    ):  # 找k個最相似的
        # unrated_products = user_item_matrix.loc[user_id, :].isna()  # 未瀏覽過
        unrated_products = user_item_matrix.loc[user_id, :].isna() | (
            user_item_matrix.loc[user_id, :] < 5
        )
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
        # unrated_products = user_item_matrix.loc[user_id, :].isna()  # 未瀏覽過
        unrated_products = user_item_matrix.loc[user_id, :].isna() | (
            user_item_matrix.loc[user_id, :] < 5
        )
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
        self.RawuserId = self.user_matrix.RawuserID
        self.buy_yes_matrix = self.user_matrix.buynummatrix

    def process_recommendation(self, userId):
        self.rs.martix_to_similarity(self.user_matrix.nummatrix)
        recommendations = self.rs.recommend_similarity(
            userId,
            self.rs.user_similarity,
            self.user_matrix.last_matrix,
            self.k,
        )
        print("推薦結果")
        for salepage_id, i in zip(
            recommendations[1], range(1, len(recommendations[1]) + 1)
        ):
            salepage_title = self.product_name.get_salepage_title(salepage_id)
            # print(f"推薦第{i}名為：{salepage_title} ")

        all_user_Id = self.user_matrix.RawuserID
        user_of_recommendation = [all_user_Id[i] for i in recommendations[0]]
        # print(f"Group ID:{user_of_recommendation}")

        return user_of_recommendation, recommendations[1]

    def process_recomm_comparing(self, userId, first_of_user):
        self.find_index = [
            index
            for index, value in enumerate(self.user_matrix.RawuserID)
            if value in first_of_user
        ]
        # print(self.find_index)
        print("Group AA in the Second Time")
        recommendations_comparing = self.rs.recommend_compareing(
            userId,
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

    def check_bought(self, userId, recommend_list):
        target_index = self.RawuserId.index(userId)
        target = self.buy_yes_matrix.iloc[target_index]
        target = target[target == 1].index.tolist()
        result = [item for item in recommend_list if item in target]
        total_product.append(result)
        if len(result) > 0:
            accuracy = len(result) / len(recommend_list) * 100
            return accuracy
        else:
            print("沒有猜中")
            return 0

    def find_user_index(self, userId):
        targer_index = self.RawuserId.index(userId)
        return targer_index
