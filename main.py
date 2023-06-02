import statistics
from data_pre_processing import UserItem, ProductName
from recommend_system import Recommend_system
from Execute_system import ExecuteSystem
import pandas as pd

if __name__ == "__main__":
    """
    k為決定推薦幾名
    data1 放測試的
    data2 放驗證的資料集
    """

    k = 12

    total_product = []

    execute_system = ExecuteSystem(
        "testid_1.xlsx",
        "SalePageData.csv",
        k,
        total_product,
        "testid_1.xlsx",
    )

    accuracy = []
    df = pd.DataFrame(columns=execute_system.user_matrix.allitem)
    df["userid"] = execute_system.RawuserId

    for i in execute_system.RawuserId:
        userId_index = execute_system.find_user_index(i)
        salepageid_of_BB = execute_system.process_recommendation(userId_index)

        for product_id in salepageid_of_BB[1]:
            df.loc[df["userid"] == i, product_id] = 1

        check_bought_record = execute_system.check_bought(i, salepageid_of_BB[1])
        print(f"準確率：{check_bought_record}%")
        accuracy.append(check_bought_record)

    print(len(accuracy))
    print(accuracy)
    print((f"全用戶平均:{statistics.mean(accuracy):.3f}%"))
    df.set_index("userid", inplace=True)
    df.fillna(0, inplace=True)
    df.to_excel("recommendation_result.xlsx")
    print(df)
