import pandas
import pymysql
from sqlalchemy import create_engine

import data_save

# 데이터 불러오기 함수
def db_pull_out(dataframe,sql_pswd):
    engine = data_save.sql_setting_Alchemy(sql_pswd)
    query = f"SELECT * FROM {dataframe}"
    return engine,query

# 데이터 결합해서 불러오기 함수
def db_select_out(dataframe1,dataframe2,group_column,sql_pswd):
    engine = data_save.sql_setting_Alchemy(sql_pswd)
    query = f"SELECT * FROM {dataframe1}"
    return engine,query