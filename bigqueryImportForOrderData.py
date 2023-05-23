import pandas as pd
import dask.dataframe as dd
import gcsfs
from pandas_gbq import to_gbq
from google.oauth2.service_account import Credentials

import os

#/* GCS Pre-Define */
projectName= "My First Project"
projectDataset = "91app_dataset"
datasetPath = "Behaviordata"
dataFileFullPath = "gs://91app_dataset/OrderData.csv"

#/* GCS API */
gcsAPI = "./lustrous-setup-386509_GCS_API_Key.json"
gbqAPI = "./lustrous-setup-386509_GBQ_API_Key.json"

# /* 連接至 GCS */
fs = gcsfs.GCSFileSystem(project=projectName,token=gcsAPI)

# /* dask */
#/* datatype 轉換錯誤，靜態設置  */
dtypes={'ChannelDetail': 'object',
       'PaymentType': 'object',
       'ShippingType': 'object'}

# /* dataFileFullPath 為直接指定需要匯入之 CSV 的 GCS 的路徑 */
# /* low_memory 為關閉 pandas 對 dtype 的推測(很佔記憶體空間) */
ddf = dd.read_csv(dataFileFullPath, dtype=dtypes, storage_options={"token": gcsAPI}, low_memory=False)

# /* dask to pandas */
df_pd = ddf.compute()

# /* import to bigquery */
credentials = Credentials.from_service_account_file(gbqAPI)
projectID = "lustrous-setup-386509"
dataBaseName = "91appdata"
tableName = "OrderData"
to_gbq(df_pd, dataBaseName+"."+tableName, project_id=projectID, credentials=credentials, if_exists='replace')