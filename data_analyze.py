import pandas as pd
import pymysql
from sqlalchemy import create_engine

import data_save
import data_read

# 로우데이터 읽기
customer_df = data_read.csv_read("Customer.csv") #고객ID(USER_####), 고객성별(남/여), 고객지역, 가입기간(월)
discount_df = data_read.csv_read("Discount.csv") #월별 정보(JAN 등으로 표시), 제품 카테고리(불규칙적), 쿠폰코드, 할인률(%)
marketing_df = data_read.csv_read("Marketing.csv") #마케팅날짜, 온/오프라인 마케팅비용(원)
onlinesales_df = data_read.csv_read("Onlinesales.csv") #고객ID, 거래ID(Transaction_#####), 거래날짜, 제품ID(Product_####) 제품카테고리, 주문수량, 단위가격(원), 배송비용(원), 할인쿠폰 적용여부

# 데이터 클랜징
df_list = [customer_df, discount_df, marketing_df, onlinesales_df]
df_name_list = ["customer_df", "discount_df", "marketing_df", "onlinesales_df"]
for i in df_list:
    data_read.na_cleaning(i)    

# 날짜 형식변환
data_read.to_date(marketing_df, "날짜")
data_read.to_date(onlinesales_df,"거래날짜")
# 칼럼명 수정(거래날짜)
onlinesales_df.rename(columns={"거래날짜":"날짜"}, inplace=True)

# 할인정보 월 데이터 변환 
month_mapping = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
discount_df["월"] = discount_df["월"].apply(lambda x: pd.to_datetime(month_mapping[x], format='%m'))
data_read.month_mapping(discount_df,"월")

# 월 데이터 추출
data_read.month_mapping(marketing_df,"날짜")
data_read.month_mapping(onlinesales_df,"날짜")

# 고객 데이터와 온라인 판매 데이터 결합
detail_sales_df = customer_df.merge(onlinesales_df, on="고객ID")

# 온라인 판매 데이터, 마케팅 데이터 결합
detail_consum_df = onlinesales_df.merge(marketing_df, on="날짜")
if '월_y' in detail_consum_df.columns:
    detail_consum_df.drop("월_y", axis=1, inplace=True)  # 존재하는 경우만 삭제
detail_consum_df.rename(columns={"월_x":"월"}, inplace=True)

# 클랜징 후 데이터 출력
print("고객정보")
print(customer_df)
print("할인정보")
print(discount_df)
print("마케팅정보")
print(marketing_df)
print("온라인판매정보")
print(onlinesales_df)
print("고객정보 + 온라인판매정보")
print(detail_sales_df)
print("온라인판매정보+마케팅정보")
print(detail_consum_df)

# sql에 데이터를 저장할지 입력
sql_pswd=input("SQL 비밀번호를 입력해주세요: ")
data_save.save_to_db(customer_df,"customer",sql_pswd)
data_save.save_to_db(discount_df,"discount",sql_pswd)
data_save.save_to_db(marketing_df,"marketing",sql_pswd)
data_save.save_to_db(onlinesales_df,"onlinesales",sql_pswd)

conn, cursor = data_save.sql_setting(sql_pswd)
conn.commit()
conn.close()