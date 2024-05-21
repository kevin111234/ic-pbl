import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras import models
from keras import layers
from matplotlib import font_manager, rc
from matplotlib import pyplot as plt

import data_frame

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

# 데이터 로드
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer_onlinesales(sql_pswd)
customer_onlinesales_df = data_frame.customer_onlinesales_df

# 데이터 전처리
customer_onlinesales_df['날짜'] = pd.to_datetime(customer_onlinesales_df['날짜'])
customer_onlinesales_df.set_index('날짜', inplace=True)
customer_onlinesales_df = customer_onlinesales_df[['고객ID','성별','가입기간','제품ID','제품카테고리','수량','평균금액','배송료','쿠폰상태'
                                                    ,'고객지역_California','고객지역_Chicago','고객지역_New Jersey','고객지역_New York','고객지역_Washington DC']]
customer_onlinesales_df.columns=['고객ID','고객ID_x','성별','가입기간','제품ID','제품카테고리','수량','평균금액','배송료','쿠폰상태'
                                                    ,'고객지역_California','고객지역_Chicago','고객지역_New Jersey','고객지역_New York','고객지역_Washington DC']
customer_onlinesales_df = customer_onlinesales_df[['고객ID','성별','가입기간','제품ID','제품카테고리','수량','평균금액','배송료','쿠폰상태'
                                                    ,'고객지역_California','고객지역_Chicago','고객지역_New Jersey','고객지역_New York','고객지역_Washington DC']]
customer_onlinesales_df = customer_onlinesales_df.dropna()

# 원-핫 인코딩 실행 후 데이터 병합
categorical_df = customer_onlinesales_df[['성별','쿠폰상태']] 
encoded_df = pd.get_dummies(categorical_df) 
encoded_df.index = customer_onlinesales_df.index
customer_onlinesales_df = pd.concat([customer_onlinesales_df, encoded_df], axis=1)
customer_onlinesales_df = customer_onlinesales_df.drop(columns=['성별','쿠폰상태'])

print(customer_onlinesales_df)

# 일자별 판매량 집계
daily_sales_df = customer_onlinesales_df.groupby('날짜')['수량'].sum().reset_index()
print(daily_sales_df)

