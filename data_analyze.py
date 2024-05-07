import pandas as pd
import pymysql
from sqlalchemy import create_engine

# 로우데이터 읽기
encoding = "cp949"
customer_df = pd.read_csv("Customer.csv",encoding=encoding) #고객ID(USER_####), 고객성별(남/여), 고객지역, 가입기간(월)
discount_df = pd.read_csv("Discount.csv",encoding=encoding) #월별 정보(JAN 등으로 표시), 제품 카테고리(불규칙적), 쿠폰코드, 할인률(%)
marketing_df = pd.read_csv("Marketing.csv",encoding=encoding) #마케팅날짜, 온/오프라인 마케팅비용(원)
onlinesales_df = pd.read_csv("Onlinesales.csv",encoding=encoding) #고객ID, 거래ID(Transaction_#####), 거래날짜, 제품ID(Product_####) 제품카테고리, 주문수량, 단위가격(원), 배송비용(원), 할인쿠폰 적용여부

# 데이터 클랜징
# 결측값 확인
customer_결측값_비율 = customer_df.isna().sum() / len(customer_df)
print("고객 정보 결측값 비율:",customer_결측값_비율)
discount_결측값_비율 = discount_df.isna().sum() / len(discount_df)
print("할인 정보 결측값 비율:", discount_결측값_비율)
marketing_결측값_비율 = marketing_df.isna().sum() / len(marketing_df)
print("마케팅 정보 결측값 비율:", marketing_결측값_비율)
online_결측값_비율 = onlinesales_df.isna().sum() / len(onlinesales_df)
print("온라인 판매 정보 결측값 비율:", online_결측값_비율)

if customer_결측값_비율.any()>0:
    print("customer_df의 결측값이 존재합니다. 해당 행을 삭제합니다.")
    customer_df.dropna(inplace=True)
if discount_결측값_비율.any()>0:
    print("discount_df의 결측값이 존재합니다. 해당 행을 삭제합니다.")
    discount_df.dropna(inplace=True)
if marketing_결측값_비율.any()>0:
    print("marketing_df의 결측값이 존재합니다. 해당 행을 삭제합니다.")
    marketing_df.dropna(inplace=True)
if online_결측값_비율.any()>0:
    print("onlinesales_df의 결측값이 존재합니다. 해당 행을 삭제합니다.")
    onlinesales_df.dropna(inplace=True)

# 날짜 형식변환
marketing_df["날짜"] = pd.to_datetime(marketing_df["날짜"])
onlinesales_df["거래날짜"] = pd.to_datetime(onlinesales_df["거래날짜"])

# 할인정보 월 데이터 변환
month_mapping = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
discount_df["월"] = discount_df["월"].apply(lambda x: pd.to_datetime(month_mapping[x], format='%m'))
discount_df["월"] = discount_df["월"].astype(str)
discount_df["월"] = discount_df["월"].str[5:7].astype(int)

# 칼럼명 수정(거래날짜, 마케팅정보 날짜)
onlinesales_df.rename(columns={"거래날짜":"날짜"}, inplace=True)

# 월 데이터 추출
discount_df["월"] = discount_df["월"].astype(int)
marketing_df["월"] = marketing_df["날짜"].astype(str)
marketing_df["월"] = marketing_df["월"].str[5:7].astype(int)
onlinesales_df["월"] = onlinesales_df["날짜"].astype(str)
onlinesales_df["월"] = onlinesales_df["월"].str[5:7].astype(int)

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
while True:
    sql_save = input("데이터를 DB에 저장하시겠습니까?(y/n): ")
    if sql_save=="y":
        print("데이터를 DB에 저장합니다")
        break
    elif sql_save=="n":
        print("데이터를 저장하지 않습니다")
        break
    else:
        print("잘못된 입력입니다. 다시 입력해주세요.")
