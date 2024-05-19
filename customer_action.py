import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

import data_frame

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

# 데이터 로드 및 준비
# data_frame.all_data() 함수는 사용자 정의 함수로, 실제 데이터 로드 방식에 맞게 조정하세요.
data_frame.all_data()
df = data_frame.customer_onlinesales_all_df

# 날짜 정보에서 연도, 월, 요일 추출
df['날짜'] = pd.to_datetime(df['날짜'])
df['Year'] = df['날짜'].dt.year
df['Month'] = df['날짜'].dt.month
df['Day'] = df['날짜'].dt.day
df['Weekday'] = df['날짜'].dt.weekday

# RFM 분석
today_date = df['날짜'].max() + pd.Timedelta(days=1)
df['Recency'] = (today_date - df['날짜']).dt.days
df['Frequency'] = df.groupby(['고객ID', '제품카테고리'])['날짜'].transform('count')
df['Monetary'] = df.groupby(['고객ID', '제품카테고리'])['구매금액'].transform('sum')

# 카테고리별 RFM 분석 결과
rfm_df = df[['고객ID', 'Recency', 'Frequency', 'Monetary']].drop_duplicates()

# 라벨 인코딩 (성별 및 고객지역)
label_encoders = {}
for column in ['성별', '고객지역']:
    label_encoders[column] = LabelEncoder()
    df[column] = label_encoders[column].fit_transform(df[column])

# 고객 행동 분석을 위한 데이터 준비
behavior_features = ['Recency', 'Frequency', 'Monetary']
behavior_data = rfm_df[behavior_features]

# 데이터 스케일링
scaler = StandardScaler()
behavior_data_scaled = scaler.fit_transform(behavior_data)

# K-means 클러스터링
kmeans = KMeans(n_clusters=5, random_state=42)
rfm_df['Cluster'] = kmeans.fit_predict(behavior_data_scaled)

# 클러스터 레이블을 원본 데이터에 추가
df = df.merge(rfm_df[['고객ID', 'Cluster']], on='고객ID', how='left')

# 클러스터별 구매 금액 시각화
plt.figure(figsize=(10, 6))
sns.boxplot(x='Cluster', y='구매금액', data=df)
plt.title('Cluster vs Purchase Amount')
plt.xlabel('Cluster')
plt.ylabel('Purchase Amount')
plt.show()

# 클러스터별 고객 수 시각화
plt.figure(figsize=(10, 6))
sns.countplot(x='Cluster', data=df)
plt.title('Number of Customers in Each Cluster')
plt.xlabel('Cluster')
plt.ylabel('Number of Customers')
plt.show()

# 클러스터와 성별, 지역에 따른 시각화
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
sns.countplot(x='Cluster', hue='성별', data=df)
plt.title('Cluster vs Gender')
plt.xlabel('Cluster')
plt.ylabel('Count')

plt.subplot(1, 2, 2)
sns.countplot(x='Cluster', hue='고객지역', data=df)
plt.title('Cluster vs Region')
plt.xlabel('Cluster')
plt.ylabel('Count')

plt.tight_layout()
plt.show()