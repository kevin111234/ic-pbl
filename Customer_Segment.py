import data_frame
import pandas as pd

#기본 데이터 로드
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer(sql_pswd)
data_frame.marketing(sql_pswd)
data_frame.discount(sql_pswd)
data_frame.onlinesales(sql_pswd)
customer_df = data_frame.customer_df
marketing_df = data_frame.marketing_df
discount_df = data_frame.discount_df
onlinesales_df = data_frame.onlinesales_df

#데이터 전처리
    #ID 형식들 숫자로 변환
customer_df['고객ID'] = customer_df['고객ID'].astype(str).str[5:]
customer_df['고객ID'] = customer_df['고객ID'].astype(int)
onlinesales_df['고객ID'] = onlinesales_df['고객ID'].astype(str).str[5:]
onlinesales_df['고객ID'] = onlinesales_df['고객ID'].astype(int)
onlinesales_df['제품ID'] = onlinesales_df['제품ID'].astype(str).str[8:]
onlinesales_df['거래ID'] = onlinesales_df['거래ID'].astype(str).str[12:]
onlinesales_df['거래ID'] = onlinesales_df['거래ID'].astype(int)
    #제품ID랑 카테고리 연결
onlinesales_df['제품ID'] = onlinesales_df['제품카테고리']+" "+onlinesales_df['제품ID']

#텍스트데이터 벡터로 변환 (제품카테고리, 고객지역)

#필요시 원-핫 인코딩(성별)

#코사인유사도 계산

#모델 형성

#모델 학습

#고객 분류

#고객군별 특성
    #데이터 추출
    #데이터 시각화