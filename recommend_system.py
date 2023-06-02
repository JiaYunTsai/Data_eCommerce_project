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


def build_recommendation_system(user_matrix):
    rs = Recommend_system()
    rs.martix_to_similarity(user_matrix.nummatrix)
    return rs
