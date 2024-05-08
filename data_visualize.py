import pandas as pd
from sqlalchemy import create_engine
import pymysql

import data_save

# SQL에서 데이터 들고오기
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
engine,query = data_save.db_pull_out("customer_info", sql_pswd)
customer_df = pd.read_sql(query, engine)
engine,query = data_save.db_pull_out("discount_info", sql_pswd)
discount_df = pd.read_sql(query, engine)
engine,query = data_save.db_pull_out("marketing_info", sql_pswd)
marketing_df = pd.read_sql(query, engine)
engine,query = data_save.db_pull_out("onlinesales_info", sql_pswd)
onlisesales_df = pd.read_sql(query, engine)
engine.dispose()

# SQL에서 데이터 결합해서 들고오기

# 데이터 분석해서 여러 형태로 변환

# 분석 결과 시각화