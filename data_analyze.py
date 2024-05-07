import pandas as pd
import pymysql
from sqlalchemy import create_engine

customer_df = pd.read_csv("Customer.csv") #고객ID, 고객성별, 고객지역, 가입기간(월)
discount_df = pd.read_csv("Discount.csv") #월별 정보, 제품 카테고리, 쿠폰코드, 할인률
marketing_df = pd.read_csv("Marketing.csv") #마케팅날짜, 온/오프라인 마케팅비용(원)
onlinesales_df = pd.read_csv("Onlinesales.csv") #고객ID, 거래ID, 거래날짜, 제품카테고리, 주문수량, 단위가격(원), 배송비용(원), 할인쿠폰 적용여부
