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

    k = []
    for j in k:
        total_product = []

        execute_system = ExecuteSystem(
            "data1.csv",
            j,
            total_product,
            "data2.csv",
        )

        accuracy = []
        accuracy_real = []
        stata = {}
        df = pd.DataFrame(columns=execute_system.user_matrix.allitem)
        df["userid"] = execute_system.RawuserId
        # df_real = pd.DataFrame(columns=execute_system.user_matrix.allitem)
        # df_real["userid"] = execute_system.allbuynummatrix.index

        for i in execute_system.RawuserId:
            userId_index = execute_system.find_user_index(i)
            salepageid_of_BB = execute_system.process_recommendation(userId_index)

            for product_id in salepageid_of_BB[1]:
                df.loc[df["userid"] == i, product_id] = 1

            check_bought_record = execute_system.check_bought(i, salepageid_of_BB[1])
            print(f"準確率：{check_bought_record}%")
            accuracy.append(check_bought_record)

            check_bought_record = execute_system.check_bought_only(
                i, salepageid_of_BB[1]
            )
            print(f"準確率：{check_bought_record}%")
            if check_bought_record != None:
                accuracy_real.append(check_bought_record)

        # print(len(accuracy))
        print(accuracy)
        print(accuracy_real)
        print((f"全用戶平均:{statistics.mean(accuracy):.3f}%"))
        print((f"真是購買用戶平均:{statistics.mean(accuracy_real):.3f}%"))
        df.set_index("userid", inplace=True)
        df.fillna(0, inplace=True)
        df.to_excel(f"recommendation_result{j}.xlsx")
    # print(df)
