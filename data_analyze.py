import pandas as pd
from sqlalchemy import create_engine

import csv_read

# 로우데이터 읽기
customer_df = csv_read.csv_read("Customer.csv") #고객ID(USER_####), 고객성별(남/여), 고객지역, 가입기간(월)
discount_df = csv_read.csv_read("Discount.csv") #월별 정보(JAN 등으로 표시), 제품 카테고리(불규칙적), 쿠폰코드, 할인률(%)
marketing_df = csv_read.csv_read("Marketing.csv") #마케팅날짜, 온/오프라인 마케팅비용(원)
onlinesales_df = csv_read.csv_read("Onlinesales.csv") #고객ID, 거래ID(Transaction_#####), 거래날짜, 제품ID(Product_####) 제품카테고리, 주문수량, 단위가격(원), 배송비용(원), 할인쿠폰 적용여부

# 데이터 클랜징
df_list = [customer_df, discount_df, marketing_df, onlinesales_df]
df_name_list = ["customer_df", "discount_df", "marketing_df", "onlinesales_df"]
for i in df_list:
    csv_read.na_cleaning(i)    

# 날짜 형식변환
csv_read.to_date(marketing_df, "날짜")
csv_read.to_date(onlinesales_df,"거래날짜")
# 칼럼명 수정(거래날짜)
onlinesales_df.rename(columns={"거래날짜":"날짜"}, inplace=True)

# 할인정보 월 데이터 변환 
month_mapping = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
discount_df["월"] = discount_df["월"].apply(lambda x: pd.to_datetime(month_mapping[x], format='%m'))
csv_read.month_mapping(discount_df,"월")

# 월 데이터 추출
csv_read.month_mapping(marketing_df,"날짜")
csv_read.month_mapping(onlinesales_df,"날짜")