import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import data_frame

# 데이터 로드
data_frame.all_data()
RFM_df = data_frame.customer_onlinesales_all_df
RFM_df["날짜"]= pd.to_datetime(RFM_df['날짜'])

# 컬럼명 확인
print(RFM_df.columns)

# Recency 계산
today_date = RFM_df['날짜'].max() + pd.Timedelta(days=1)

# RFM 분석을 위한 그룹화
recency_df = RFM_df.groupby('고객ID')['날짜'].max().reset_index()
recency_df['Recency'] = (today_date - recency_df['날짜']).dt.days

frequency_df = RFM_df.groupby('고객ID')['날짜'].count().reset_index()
frequency_df.rename(columns={'날짜': 'Frequency'}, inplace=True)

monetary_df = RFM_df.groupby('고객ID')['구매금액'].sum().reset_index()
monetary_df.rename(columns={'구매금액': 'Monetary'}, inplace=True)

# RFM 테이블 결합
rfm_table = recency_df.merge(frequency_df, on='고객ID').merge(monetary_df, on='고객ID')

# RFM 점수 계산 (각 항목별 점수: 1에서 5까지)
rfm_table['R_Score'] = pd.qcut(rfm_table['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm_table['F_Score'] = pd.qcut(rfm_table['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm_table['M_Score'] = pd.qcut(rfm_table['Monetary'], 5, labels=[1, 2, 3, 4, 5])

# RFM 점수를 합쳐서 RFM Segment를 생성
rfm_table['RFM_Segment'] = rfm_table['R_Score'].astype(str) + rfm_table['F_Score'].astype(str) + rfm_table['M_Score'].astype(str)

# RFM 점수 합계
rfm_table['RFM_Score'] = rfm_table[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

# RFM Score 분포 시각화
plt.figure(figsize=(12, 6))
sns.histplot(rfm_table['RFM_Score'], bins=20, kde=True)
plt.title('RFM Score Distribution')
plt.xlabel('RFM Score')
plt.ylabel('Frequency')
plt.show()

# RFM Segment 분포 시각화
plt.figure(figsize=(12, 6))
sns.countplot(x='RFM_Segment', data=rfm_table, order=rfm_table['RFM_Segment'].value_counts().index)
plt.title('RFM Segment Distribution')
plt.xlabel('RFM Segment')
plt.ylabel('Number of Customers')
plt.xticks(rotation=90)
plt.show()