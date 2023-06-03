import statistics
from data_pre_processing import UserItem, ProductName
from recommend_system import Recommend_system
from Execute_system import ExecuteSystem
import pandas as pd
import random

if __name__ == "__main__":
    """
    k為決定推薦幾名
    data1 放測試的
    data2 放驗證的資料集
    """

    k = 12

    total_product = []

    execute_system = ExecuteSystem(
        "data_march.csv",
        "SalePageData.csv",
        k,
        total_product,
        "Answer.csv",
    )

    accuracy = []
    df = pd.DataFrame(columns=execute_system.user_matrix.allitem)
    df["userid"] = execute_system.RawuserId
    df.set_index("userid", inplace=True)
    with open("random_group.txt", "r") as file:
        random_group_data = [line.strip() for line in file]

    random_sample = random.sample(random_group_data, k=10)
    random_sample = [item.strip() for item in random_sample]
    # print(random_sample)
    # print(execute_system.RawuserId)ㄥ
    for i in random_sample:
        userId_index = execute_system.find_user_index(i)
        if userId_index is None:
            print(f"Skipping recommendations for user {i}")
            continue
        salepageid_of_BB = execute_system.process_recommendation(userId_index)

        for product_id in salepageid_of_BB[1]:
            df.loc[df.index == i, product_id] = 1

        check_bought_record = execute_system.check_bought(i, salepageid_of_BB[1])
        print(f"準確率：{check_bought_record}%")
        accuracy.append(check_bought_record)

    print(accuracy)
    if len(accuracy) > 0:
        print((f"全用戶平均:{statistics.mean(accuracy):.3f}%"))
    else:
        print("抽到太多無行為用戶")
    df.fillna(0, inplace=True)
    df.to_excel("recommendation_result.xlsx")
    # print(df)
