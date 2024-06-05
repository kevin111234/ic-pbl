# 모듈 불러오기
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
import numpy as np
from sklearn.model_selection import train_test_split
from keras import models
from keras import layers
from keras import callbacks
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt
from matplotlib import font_manager, rc
from sklearn.metrics import silhouette_score

import data_save
import data_frame

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

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
print(reduced_features_train)

# 고객 세분화
# K-means 클러스터링 활용
# 0. 데이터 스케일링
# 데이터 표준화 (스케일링)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

silhouettes = []
silhouette_x = []
for k in range(2, 30):  # K 값 범위 설정 (2부터 10까지)
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(X_scaled)
    silhouettes.append(silhouette_score(X_scaled, kmeans.labels_))
    silhouette_x.append(k)
largest_number = max(silhouettes)
largest_index = silhouettes.index(largest_number)
# Silhouette score 그래프 출력
plt.plot(range(2, 30), silhouettes, marker='o')
plt.xlabel('Number of clusters (K)')
plt.ylabel('Silhouette score')
plt.show()
largest_index = 6
largest_number = 6

# K-means 클러스터링, 학습
kmeans = KMeans(n_clusters=largest_index+2, random_state=0)
kmeans.fit(X_scaled)
cluster_labels = kmeans.labels_  # 클러스터 레이블을 변수에 할당

# 클러스터 레이블을 원본 데이터프레임에 추가
rfm_df_filtered['Cluster'] = cluster_labels

# 클러스터별 RFM 변수 및 제품 카테고리 평균 계산
cluster_avg = rfm_df_filtered.groupby('Cluster')[['최근구매일자', '구매빈도', '총구매금액', 'AveragePurchaseValue'] + list(rfm_df_filtered.columns[7:27])].mean().round(2)
customer_segment = rfm_df_filtered[['고객ID', 'Cluster']]
print(customer_segment)

# 결과 출력 (전치 후 출력)
print(cluster_avg.T)

for i in range(largest_index + 2):
    cluster_data = rfm_df_filtered[rfm_df_filtered['Cluster'] == i]
    print(f"\nCluster {i}:")
    print(f"  - 고객 수: {len(cluster_data)}")
    print(f"  - 최근구매일자 평균: {cluster_data['최근구매일자'].mean():.2f}")
    print(f"  - 구매빈도 평균: {cluster_data['구매빈도'].mean():.2f}")
    print(f"  - 총구매금액 평균: {cluster_data['총구매금액'].mean():.2f}")
    print(f"  - 평균구매금액 평균: {cluster_data['AveragePurchaseValue'].mean():.2f}")
    print("-" * 20)

# 5. 클러스터별 평균 값 시각화
cluster_avg = rfm_df_filtered.groupby('Cluster')[['최근구매일자', '구매빈도', '총구매금액', 'AveragePurchaseValue']].mean().round(2)

# 클러스터별 평균 값 막대 그래프 시각화
colors = ['#FAEDDA', '#AEE8CA', '#6ACFC9', '#26B6C6']
plt.figure(figsize=(12, 8))
for i, col in enumerate(cluster_avg.columns):
    plt.subplot(2, 2, i + 1)  # 2x2 subplot 생성
    cluster_avg[col].plot(kind='bar', rot=0, color=colors[i])
    plt.title(f'Cluster Average - {col}')
    plt.xlabel('Cluster')
    plt.ylabel(col)

plt.tight_layout()
plt.show()

# 1. 클러스터별 인구 통계학적 정보 분석
demographic_cols = ['성별', '고객지역']  # 분석할 인구 통계학적 정보 열
for col in demographic_cols:
    print(f"\n{col}별 고객 분포:")
    for cluster in rfm_df_filtered['Cluster'].unique():
        cluster_data = rfm_df_filtered[rfm_df_filtered['Cluster'] == cluster]
        print(f"  - Cluster {cluster}: {cluster_data[col].value_counts(normalize=True).round(2)}")

    # 막대 그래프 시각화
    rfm_df_filtered.groupby('Cluster')[col].value_counts().unstack().plot(kind='bar', rot=0)
    plt.title(f'Cluster Distribution by {col}')
    plt.xlabel('Cluster')
    plt.ylabel('Count')
    plt.show()

# 클러스터별 제품 카테고리 구매 비율 계산 및 시각화
category_columns = list(rfm_df_filtered.columns[7:27])
cluster_colors = ['#5068F2', '#6683D9', '#FA7F08', '#F24405', '#BAA0F2', '#9340E8','#8CDB50','#66CC1F']  # 클러스터별 색상 지정

for cluster in rfm_df_filtered['Cluster'].unique():
    cluster_data = rfm_df_filtered[rfm_df_filtered['Cluster'] == cluster]
    cluster_size = len(cluster_data)
    category_sums = cluster_data[category_columns].sum()
    category_ratios = (category_sums / cluster_size).sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    category_ratios.plot(kind='bar', rot=90, color=cluster_colors[cluster])  # 클러스터별 색상 적용
    plt.title(f'Cluster {cluster} - Product Category Purchase Ratios')
    plt.xlabel('Product Category')
    plt.ylabel('Average Purchase Ratio')
    plt.show()

# 데이터베이스에 분류결과 저장
"""data_frame.customer(sql_pswd)
customer_info = data_frame.customer_df
customer_info = pd.merge(customer_info, customer_segment, on='고객ID', how='left')
customer_info = customer_info[["고객ID","성별","고객지역","가입기간","고객분류1","Cluster"]]
data_save.save_to_db(customer_info, "customer", sql_pswd)"""