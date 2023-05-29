import pandas as pd


def merger_csv(previous_file, new_file):
    df1 = pd.read_csv(previous_file)
    df2 = pd.read_csv(new_file)

    columns_need = ['ShopMemberId', 'Behavior', 'SalePageId',]
    df1 = df1[columns_need]
    df2 = df2[columns_need]

    merger_df = pd.concat([df1, df2])

    return merger_df
