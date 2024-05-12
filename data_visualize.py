import pandas as pd
from sqlalchemy import create_engine
import pymysql

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

# 2테이블 결합
# 고객정보 판매정보 결합
engine,query = data_output.db_group_1column("*","customer_info", "onlinesales_info", "고객ID", sql_pswd)
customer_onlinesales_df = pd.read_sql(query, engine)
#할인정보 판매정보 결합
engine,query = data_output.db_group_2column("*","discount_info", "onlinesales_info", "월", "제품카테고리", sql_pswd)
discount_onlinesales_df = pd.read_sql(query, engine)
# 마케팅정보 판매정보 결합
engine,query = data_output.db_group_1column("*","marketing_info", "onlinesales_info", "날짜", sql_pswd)
marketing_onlinesales_df = pd.read_sql(query, engine)

# 추가 세부자료
# 카테고리별 고객 구매정보
engine,query = data_output.db_group_1column("customer_info.고객ID, 제품카테고리, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.고객ID, onlinesales_info.제품카테고리 ORDER BY 고객ID DESC, 구매금액 DESC")
individual_customer_df = pd.read_sql(query, engine)
# 월별 고객 구매정보
engine,query = data_output.db_group_1column("customer_info.고객ID, 월, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.고객ID, onlinesales_info.월 ORDER BY 고객ID DESC, 월 ASC, 구매금액 DESC")
month_customer_df = pd.read_sql(query, engine)
# 고객지역별 카테고리 구매정보
engine,query = data_output.db_group_1column("customer_info.고객지역, 제품카테고리, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.고객지역, onlinesales_info.제품카테고리 ORDER BY 고객지역 DESC, 구매금액 DESC")
local_customer_df = pd.read_sql(query, engine)
# 고객지역별 구매정보
engine,query = data_output.db_group_1column("customer_info.고객지역, COUNT(*)AS 고객_수, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.고객지역 ORDER BY 고객지역 DESC, 구매금액 DESC")
local_df = pd.read_sql(query, engine)
# 가입기간별 카테고리 구매정보
engine,query = data_output.db_group_1column("customer_info.가입기간, 제품카테고리, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.가입기간, onlinesales_info.제품카테고리 ORDER BY 가입기간 DESC, 구매금액 DESC")
period_customer_df = pd.read_sql(query, engine)
# 성별별 카테고리 구매정보
engine,query = data_output.db_group_1column("customer_info.성별, 제품카테고리, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.성별, onlinesales_info.제품카테고리 ORDER BY 구매금액 DESC")
gender_customer_df = pd.read_sql(query, engine)
# 성별별 구매정보
engine,query = data_output.db_group_1column("customer_info.성별, COUNT(*)AS 고객_수, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.성별 ORDER BY 구매금액 DESC")
gender_df = pd.read_sql(query, engine)
# 월별 구매정보
engine,query = data_output.db_group_1column("discount_info.`월`, discount_info.`할인율`, SUM(onlinesales_info.수량)AS 수량"
                                            , "discount_info","onlinesales_info","월", sql_pswd
                                            ,"GROUP BY discount_info.월, discount_info.`할인율` ORDER BY 월 ASC")
month_discount_df = pd.read_sql(query, engine)
# 할인율별 구매정보
engine,query = data_output.db_group_1column("discount_info.`할인율`, SUM(onlinesales_info.수량)AS 수량, SUM(onlinesales_info.평균금액*수량+배송료)AS 구매금액"
                                            , "discount_info","onlinesales_info","월", sql_pswd
                                            ,"GROUP BY discount_info.`할인율` ORDER BY 할인율 ASC")
rate_discount_df = pd.read_sql(query, engine)

engine.dispose()

# 확인용 print문
# 기본 테이블
print(customer_df)
print(discount_df)
print(marketing_df)
print(onlisesales_df)

# 2테이블 결합
print("고객정보 판매정보 결합")
print(customer_onlinesales_df)
print("할인정보 판매정보 결합")
print(discount_onlinesales_df)
print("마케팅정보 판매정보 결합")
print(marketing_onlinesales_df)

# 세부결합 테이블
print("카테고리별 고객 구매정보")
print(individual_customer_df)
print("월별 고객 구매정보")
print(month_customer_df)
print("고객지역별 카테고리 구매정보")
print(local_customer_df)
print("고객지역별 구매정보")
print(local_df)
print("가입기간별 카테고리 구매정보")
print(period_customer_df)
print("성별별 카테고리 구매정보")
print(gender_customer_df)
print("성별별 구매정보")
print(gender_df)
print("월별 구매정보")
print(month_discount_df)
print("할인율별 구매정보")
print(rate_discount_df)

# 분석 결과 시각화