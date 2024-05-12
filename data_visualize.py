import pandas as pd
from sqlalchemy import create_engine
import pymysql

import data_save
import data_output

# SQL에서 데이터 들고오기
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
engine,query = data_output.db_pull_out("*","customer_info", sql_pswd)
customer_df = pd.read_sql(query, engine)
engine,query = data_output.db_pull_out("*","discount_info", sql_pswd)
discount_df = pd.read_sql(query, engine)
engine,query = data_output.db_pull_out("*","marketing_info", sql_pswd)
marketing_df = pd.read_sql(query, engine)
engine,query = data_output.db_pull_out("*","onlinesales_info", sql_pswd)
onlisesales_df = pd.read_sql(query, engine)

print(customer_df)
print(discount_df)
print(marketing_df)
print(onlisesales_df)

# 2테이블 결합
print("고객정보 판매정보 결합")
engine,query = data_output.db_group_1column("*","customer_info", "onlinesales_info", "고객ID", sql_pswd)
customer_onlinesales_df = pd.read_sql(query, engine)
print(customer_onlinesales_df)

print("할인정보 판매정보 결합")
engine,query = data_output.db_group_2column("*","discount_info", "onlinesales_info", "월", "제품카테고리", sql_pswd)
discount_onlinesales_df = pd.read_sql(query, engine)
print(discount_onlinesales_df)

print("마케팅정보 판매정보 결합")
engine,query = data_output.db_group_1column("*","marketing_info", "onlinesales_info", "날짜", sql_pswd)
marketing_onlinesales_df = pd.read_sql(query, engine)
print(marketing_onlinesales_df)


engine.dispose()

# 데이터 분석해서 여러 형태로 변환

# 분석 결과 시각화