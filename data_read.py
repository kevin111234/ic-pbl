import pandas as pd

# 데이터 클랜징
# 결측값 확인
def na_cleaning(dataframe):
    결측값_비율 = dataframe.isna().sum() / len(dataframe)
    print("결측값 비율:", 결측값_비율)
    if 결측값_비율.any()>0:
        print("DF에 결측값이 존재합니다. 해당 행을 삭제합니다.")
        dataframe.dropna(inplace=True)

#날짜 형식 변환

#월 데이터 추출