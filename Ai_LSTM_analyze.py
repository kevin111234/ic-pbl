import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras import models
from keras import layers
from matplotlib import font_manager, rc
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error

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

# 특징 선택 및 스케일링
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(daily_sales_df[['수량']])

# 시계열 데이터 분할
n_timesteps = 7  # 과거 7일 데이터를 기반으로 예측
X, y = [], []
for i in range(n_timesteps, len(scaled_data)):
    X.append(scaled_data[i-n_timesteps:i, 0])
    y.append(scaled_data[i, 0])
X, y = np.array(X), np.array(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)  # shuffle=False로 시간 순서 유지
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, shuffle=False)  # 60% train, 20% validation, 20% test

# 모델 구축
model = models.Sequential()
model.add(layers.LSTM(units=50, activation='relu', input_shape=(n_timesteps, 1)))
model.add(layers.Dropout(0.2))  # Overfitting 방지를 위한 Dropout 추가 (선택 사항)
model.add(layers.Dense(units=1))  # 예측 결과는 1개 (판매량)
model.compile(optimizer='adam', loss='mse')

# 모델 학습
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_val, y_val))

# 테스트 데이터 예측
y_pred = model.predict(X_test)

# 예측 결과를 원래 스케일로 변환
y_pred = scaler.inverse_transform(y_pred)
y_test = scaler.inverse_transform(y_test.reshape(-1, 1))  # y_test도 스케일 변환

# 평가
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f'MSE: {mse:.2f}, RMSE: {np.sqrt(mse):.2f}, MAE: {mae:.2f}')

# 시각화
plt.figure(figsize=(10, 6))
plt.plot(daily_sales_df.index[-len(y_test):], y_test, label='Actual')
plt.plot(daily_sales_df.index[-len(y_test):], y_pred, label='Predicted')
plt.title('Daily Sales Prediction')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.legend()
plt.show()