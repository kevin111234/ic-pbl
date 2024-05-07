import pandas as pd
import pymysql
from sqlalchemy import create_engine

#로우데이터 읽기
encoding = "cp949"
customer_df = pd.read_csv("Customer.csv",encoding=encoding) #고객ID(USER_####), 고객성별(남/여), 고객지역, 가입기간(월)
discount_df = pd.read_csv("Discount.csv",encoding=encoding) #월별 정보(JAN 등으로 표시), 제품 카테고리(불규칙적), 쿠폰코드, 할인률(%)
marketing_df = pd.read_csv("Marketing.csv",encoding=encoding) #마케팅날짜, 온/오프라인 마케팅비용(원)
onlinesales_df = pd.read_csv("Onlinesales.csv",encoding=encoding) #고객ID, 거래ID(Transaction_#####), 거래날짜, 제품ID(Product_####) 제품카테고리, 주문수량, 단위가격(원), 배송비용(원), 할인쿠폰 적용여부

#로우데이터 출력
print("고객정보")
print(customer_df)
print("할인정보")
print(discount_df)
print("마케팅정보")
print(marketing_df)
print("온라인판매정보")
print(onlinesales_df)

#데이터 클랜징
#형식변환
marketing_df["날짜"] = pd.to_datetime(marketing_df["날짜"])
onlinesales_df["거래날짜"] = pd.to_datetime(onlinesales_df["거래날짜"])
#할인정보 월 데이터 변환
month_mapping = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
discount_df["월"] = discount_df["월"].apply(lambda x: 
                                                    pd.to_datetime(month_mapping[x], format='%m'))
discount_df["월_기간"] = discount_df["월"].dt.to_period("M", starting_year=2019)
#칼럼명 수정(거래날짜, 마케팅정보 날짜)


#클랜징 후 데이터 출력
print("고객정보")
print(customer_df)
print("할인정보")
print(discount_df)
print("마케팅정보")
print(marketing_df)
print("온라인판매정보")
print(onlinesales_df)