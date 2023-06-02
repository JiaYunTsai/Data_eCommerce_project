import statistics
from data_pre_processing import UserItem
from data_pre_processing import ProductName
from recommend_system import Recommend_system


class ExecuteSystem:
    def __init__(self, behavior_data, salepage_data, number_of_product, total_product):
        self.user_matrix = UserItem(behavior_data)
        self.user_matrix.user_item_dict()
        self.user_matrix.martix()
        self.product_name = ProductName(salepage_data)
        self.rs = Recommend_system()
        self.k = number_of_product
        self.find_index = None
        self.RawuserId = self.user_matrix.RawuserID
        self.buy_yes_matrix = self.user_matrix.buynummatrix
        self.total_product = total_product

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
        self.total_product.append(result)
        if len(result) > 0:
            accuracy = len(result) / len(recommend_list) * 100
            return accuracy
        else:
            print("沒有猜中")
            return 0

    def find_user_index(self, userId):
        targer_index = self.RawuserId.index(userId)
        return targer_index


def execute_recommendation_system(execute_system):
    user_list = []
    accuracy = []
    total_product = []

    for i in execute_system.RawuserId:
        user_list.append(i)
    for j in user_list:
        userId_index = execute_system.find_user_index(j)
        salepageid_of_BB = execute_system.process_recommendation(userId_index)
        check_bought_record = execute_system.check_bought(j, salepageid_of_BB[1])
        print(f"準確率：{check_bought_record}%")
        accuracy.append(check_bought_record)
    print(accuracy)
    print((f"全用戶平均:{statistics.mean(accuracy):.3f}%"))
