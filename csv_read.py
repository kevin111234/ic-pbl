import pandas as pd

def csv_read(csv_file):
    try:
        df = pd.read_csv(f"additional_file/{csv_file}", encoding="cp949")
        return(df)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - {csv_file}")
        return None
    except pd.errors.ParserError:
        print(f"오류: CSV 파일 파싱 오류 - {csv_file}")
        return None
    

# 데이터 클랜징
# 결측값 확인
def na_cleaning(dataframe, fillna_strategy=None, threshold=None):
    결측값_비율 = dataframe.isna().sum() / len(dataframe)
    print("결측값 비율:", 결측값_비율)
    if 결측값_비율.any()>0:
        print("DF에 결측값이 존재합니다. 해당 행을 삭제합니다.")
        dataframe.dropna(inplace=True)

#날짜 형식 변환
def to_date(dataframe, column):
    dataframe[column] = pd.to_datetime(dataframe[column])

#월 데이터 추출
def month_mapping(dataframe,column):
    dataframe["월"] = dataframe[column].astype(str)
    dataframe["월"] = dataframe["월"].str[5:7].astype(int)
    dataframe["월"] = dataframe["월"].astype(int)