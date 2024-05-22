import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras import models, layers, callbacks
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
customer_onlinesales_df = customer_onlinesales_df[['고객ID', '성별', '고객분류', '제품ID', '제품카테고리', '수량', '평균금액', '배송료', '쿠폰상태']]
customer_onlinesales_df = customer_onlinesales_df.dropna()

# 원-핫 인코딩 실행 후 데이터 병합
categorical_df = customer_onlinesales_df[['성별', '고객분류', '쿠폰상태']]
encoded_df = pd.get_dummies(categorical_df)
encoded_df.index = customer_onlinesales_df.index
customer_onlinesales_df = pd.concat([customer_onlinesales_df, encoded_df], axis=1)
customer_onlinesales_df = customer_onlinesales_df.drop(columns=['성별', '고객분류', '쿠폰상태'])

# 일자별 판매량 집계
daily_sales_df = customer_onlinesales_df.groupby('날짜')['수량'].sum().reset_index()

# 시계열 데이터를 LSTM 모델 학습에 사용할 수 있는 형태로 변환
daily_sales_df.set_index('날짜', inplace=True)
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(daily_sales_df)

# 시계열 데이터를 LSTM 모델의 입력 형태로 변환하는 함수
def create_sequences(data, sequence_length):
    xs = []
    ys = []
    for i in range(len(data) - sequence_length):
        x = data[i:i+sequence_length]
        y = data[i+sequence_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

sequence_length = 7  # 예를 들어, 최근 30일의 데이터를 사용하여 다음 날의 판매량을 예측
X, y = create_sequences(scaled_data, sequence_length)

# LSTM 입력 형태에 맞게 데이터 차원 변경
X = X.reshape((X.shape[0], X.shape[1], 1))

# 학습 및 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# LSTM 모델 정의
model = models.Sequential()
model.add(layers.Input(shape=(sequence_length, 1)))
model.add(layers.LSTM(100, activation='relu', return_sequences=True))
model.add(layers.Dropout(0.2))
model.add(layers.LSTM(50, activation='relu'))
model.add(layers.Dense(1))
model.compile(optimizer='adam', loss='mse')

# 조기 종료 콜백 설정
early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# 모델 학습
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2, callbacks=[early_stopping])

# 모델 평가
y_pred = model.predict(X_test)
y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
y_pred_inv = scaler.inverse_transform(y_pred)

# 평가 지표 출력
mse = mean_squared_error(y_test_inv, y_pred_inv)
mae = mean_absolute_error(y_test_inv, y_pred_inv)
print(f'MSE: {mse}, MAE: {mae}')

# 결과 시각화
plt.figure(figsize=(12, 6))
plt.plot(daily_sales_df.index[-len(y_test):], y_test_inv, label='Actual')
plt.plot(daily_sales_df.index[-len(y_test):], y_pred_inv, label='Predicted')
plt.legend()
plt.show()