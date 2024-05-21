# 모듈 불러오기
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from keras import models
from keras import layers
from keras import callbacks

import data_frame

# 데이터 불러오기
# 구매 관련 데이터 + 고객정보
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer(sql_pswd)
data_frame.onlinesales(sql_pswd)
customer_df = data_frame.customer_df
onlinesales_df = data_frame.onlinesales_df

# 데이터 전처리
# 이상치 처리, 데이터 정규화, 원-핫 인코딩
# 데이터 통합
customer_onlinesales_df = pd.merge(customer_df, onlinesales_df, on='고객ID', how='left')
# RFM 분석 데이터 계산
# - Recency 계산: 가장 최근 구매 일자로부터 경과일 계산
customer_onlinesales_df["날짜"]= pd.to_datetime(customer_onlinesales_df['날짜'])
max_date = customer_onlinesales_df['날짜'].max()
customer_onlinesales_df['날짜'] = pd.to_datetime(customer_onlinesales_df['날짜'])
customer_onlinesales_df['Recency'] = (max_date - customer_onlinesales_df['날짜']).dt.days

# - Frequency, Monetary 계산: 고객별 구매 횟수, 총 구매 금액 계산
rfm_df = customer_onlinesales_df.groupby('고객ID').agg(
    Recency=('Recency', 'min'),  # Recency는 최솟값 (가장 최근 구매)
    Frequency=('거래ID', 'count'),
    Monetary=('평균금액', lambda x: (x * customer_onlinesales_df.loc[x.index, '수량'] + customer_onlinesales_df.loc[x.index, '배송료']).sum())
)

# 필요한 고객 정보 추가
rfm_df = rfm_df.reset_index().merge(customer_df[['고객ID', '성별', '고객지역', '가입기간']], on='고객ID', how='left')
columns_to_fill = ['Recency', 'Frequency', 'Monetary']  # 0으로 채울 열 이름 지정
rfm_df[columns_to_fill] = rfm_df[columns_to_fill].fillna(0)
rfm_df = rfm_df.dropna()

# 3. 고객 세분화 특징 데이터 생성
# - 제품 카테고리별 구매 횟수: 피벗 테이블 활용
category_df = customer_onlinesales_df.pivot_table(index='고객ID', columns='제품카테고리', values='거래ID', aggfunc='count').fillna(0)
# RFM 데이터와 제품 카테고리별 구매 횟수 데이터 병합
rfm_df = pd.merge(rfm_df, category_df, on='고객ID', how='left')
rfm_df = rfm_df.fillna(0)
# 고객ID, 구매빈도 = F, 평균구매금액 = M/F, 총구매금액 = M, 최근구매일자 = R, 구매상품카테고리, 성별, 고객지역, 가입기간
zero_frequency_rows = rfm_df[rfm_df['Frequency'] == 0] # 1. `Frequency` 값이 0인 행 식별
rfm_df_filtered = rfm_df[rfm_df['Frequency'] != 0].copy()  # 2. `Frequency` 값이 0이 아닌 행 선택
rfm_df_filtered['AveragePurchaseValue'] = rfm_df_filtered['Monetary'] / rfm_df_filtered['Frequency'] # 3. `AveragePurchaseValue` 계산
rfm_df_filtered = pd.concat([rfm_df_filtered, zero_frequency_rows]) # 4. `zero_frequency_rows` 데이터프레임 다시 추가
rfm_df_filtered['AveragePurchaseValue'] = rfm_df_filtered['AveragePurchaseValue'].fillna(0) # 5. `AveragePurchaseValue` 열의 결측값 0으로 채우기
rfm_df_filtered.columns = ['고객ID', '최근구매일자', '구매빈도', '총구매금액', '성별', '고객지역', '가입기간',
        'Accessories', 'Android', 'Apparel', 'Backpacks', 'Bags', 'Bottles',
        'Drinkware', 'Fun', 'Gift Cards', 'Google', 'Headgear', 'Housewares',
        'Lifestyle', 'More Bags', 'Nest', 'Nest-Canada', 'Nest-USA',
        'Notebooks & Journals', 'Office', 'Waze', 'AveragePurchaseValue']

# 데이터 정규화
scaler = MinMaxScaler()
rfm_df_scaled = scaler.fit_transform(rfm_df_filtered[['최근구매일자', '구매빈도', '총구매금액']])

# 원-핫 인코딩
encoder = OneHotEncoder()
encoded_categorical = encoder.fit_transform(rfm_df_filtered[['성별', '고객지역']])

# 인공신경망 모델 구축
# 오토인코더 모델 활용
# 1. 데이터 준비
X = np.hstack((rfm_df_scaled, encoded_categorical.toarray()))  # 특징 행렬 생성
X_train, X_temp = train_test_split(X, test_size=0.2, random_state=0)
X_val, X_test = train_test_split(X_temp, test_size=0.5, random_state=0)

# 2. 오토인코더 모델 구축 및 학습
input_dim = X_train.shape[1]
encoded_dim = input_dim // 2  # 은닉층 노드 수 설정 (차원 축소)

input_layer = layers.Input(shape=(input_dim,))
encoded = layers.Dense(encoded_dim, activation='relu')(input_layer)
decoded = layers.Dense(input_dim, activation='linear')(encoded)

autoencoder = models.Model(input_layer, decoded)
autoencoder.compile(optimizer='adam', loss='mse')

early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

autoencoder.fit(X_train, X_train,
                epochs=50,
                batch_size=32,
                shuffle=True,
                validation_data=(X_val, X_val),
                callbacks=[early_stopping])

# 3. 차원 축소
encoder = models.Model(input_layer, encoded)
reduced_features_train = encoder.predict(X_train)

# 4. 결과 확인
print("Reduced features shape:", reduced_features_train.shape)


# 고객 세분화
# K-means 클러스터링 활용

# 결과 해석 및 활용
