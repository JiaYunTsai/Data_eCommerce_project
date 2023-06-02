import statistics
from data_pre_processing import UserItem, ProductName
from recommend_system import Recommend_system
from Execute_system import ExecuteSystem

if __name__ == "__main__":
    """
    k為決定推薦幾名
    userId應該沒問題，有問題就抓資料集內隨便一人
    data1 放誰都可以，這個是以購買有無當答案的
    """

    k = 12

    total_product = []

    execute_system = ExecuteSystem(
        "testid_31.xlsx", "SalePageData.csv", k, total_product
    )

    user_list = []
    accuracy = []

    for i in execute_system.RawuserId:
        user_list.append(i)
    for j in user_list:
        userId_index = execute_system.find_user_index(j)
        salepageid_of_BB = execute_system.process_recommendation(userId_index)
        check_bought_record = execute_system.check_bought(j, salepageid_of_BB[1])
        print(f"準確率：{check_bought_record}%")
        accuracy.append(check_bought_record)
    print(len(accuracy))
    print(accuracy)
    print((f"全用戶平均:{statistics.mean(accuracy):.3f}%"))
