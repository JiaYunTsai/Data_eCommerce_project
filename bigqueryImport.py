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

#/* GCS API */
gcsAPI = "./lustrous-setup-386509_GCS_API_Key.json"
gbqAPI = "./lustrous-setup-386509_GBQ_API_Key.json"

# /* 連接至 GCS */
fs = gcsfs.GCSFileSystem(project=projectName,token=gcsAPI)

# /* 取得 GCS 中的特定檔案 */
fileList = fs.ls(projectDataset+"/"+datasetPath)
_newfileList = ["gs://" + x for x in fileList]
#print(_newfileList)

# /* dask */
#/* datatype 轉換錯誤，靜態設置  */
dtypes={'DeviceId': 'object',
       'EventTime': 'float64',
       'HitTime': 'float64',
       'Version': 'object',
       'CategoryId': 'object',
       'RegisterTunnel': 'object',
      'SearchTerm': 'object',
       'TradesGroupCode': 'object',
       'ContentId': 'object',
       'ContentName': 'object',
       'ContentType': 'object',
       'PageType': 'object' }

# /* 第一個為 gs://91app_dataset/Behaviordata/，所以跳過從 1 開始 */
# /* low_memory 為關閉 pandas 對 dtype 的推測(很佔記憶體空間) */
ddf = dd.read_csv(_newfileList[1:], dtype=dtypes, storage_options={"token": gcsAPI}, low_memory=False)

# /* dask to pandas */
df_pd = ddf.compute()

# /* import to bigquery */
credentials = Credentials.from_service_account_file(gbqAPI)
projectID = "lustrous-setup-386509"
dataBaseName = "BehaviorData"
tableName = "BehaviorData"
to_gbq(df_pd, dataBaseName+"."+tableName, project_id=projectID, credentials=credentials, if_exists='replace')