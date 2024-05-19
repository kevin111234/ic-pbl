import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

import data_frame
import data_save

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

# 데이터 로드
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.all_data(sql_pswd)
RFM_df = data_frame.customer_onlinesales_all_df
RFM_df["날짜"]= pd.to_datetime(RFM_df['날짜'])

# 결측치 확인 및 처리
RFM_df = RFM_df.dropna(subset=['고객ID', '날짜', '구매금액'])

# RFM 분석을 위한 그룹화
recency_df = RFM_df.groupby('고객ID')['날짜'].max().reset_index()
recency_df['Recency'] = (recency_df['날짜'].max() - recency_df['날짜']).dt.days

frequency_df = RFM_df.groupby('고객ID')['날짜'].count().reset_index()
frequency_df.rename(columns={'날짜': 'Frequency'}, inplace=True)

monetary_df = RFM_df.groupby('고객ID')['구매금액'].sum().reset_index()
monetary_df.rename(columns={'구매금액': 'Monetary'}, inplace=True)

# RFM 테이블 결합
rfm_table = recency_df.merge(frequency_df, on='고객ID').merge(monetary_df, on='고객ID')

# RFM 점수 계산 (각 항목별 점수: 1에서 5까지)
rfm_table['R_Score'] = pd.qcut(rfm_table['Recency'], q=5, labels=[5, 4, 3, 2, 1])
rfm_table['F_Score'] = pd.qcut(rfm_table['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
rfm_table['M_Score'] = pd.qcut(rfm_table['Monetary'], q=5, labels=[1, 2, 3, 4, 5])

# RFM 점수 합계
rfm_table['RFM_Score'] = rfm_table[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

# 세그먼트 정의 함수
def segment_label(row):
    r = int(row['R_Score'])
    f = int(row['F_Score'])
    m = int(row['M_Score'])
    
    if r <= 2 and f >= 4 and m >= 4:
        return '챔피언'
    elif f >= 4 and m >= 3:
        return '충성 고객'
    elif r <= 2 and m >= 3:
        return '잠재적 충성고객'
    elif r <= 2:
        return '신규 고객'
    elif r <= 3 and m >= 2:
        return '유망 고객'
    elif r <= 3 and m < 2:
        return '관심 필요 고객'
    elif r > 3 and f >= 2:
        return '곧 이탈할 고객'
    elif r > 4 and m >= 3:
        return '위험 고객'
    elif r > 4 and m < 3:
        return "휴면 고객"
    else:
        return '이탈 고객'

rfm_table['고객분류'] = rfm_table.apply(segment_label, axis=1)

# 세그먼트 분포 확인
segment_counts = rfm_table['고객분류'].value_counts().reset_index()
segment_counts.columns = ['고객분류', '고객 수']
print(segment_counts)

# 고객 정보 데이터프레임에 세그먼트 추가
customer_info = RFM_df[['고객ID', '성별', '고객지역']].drop_duplicates()
customer_info = customer_info.merge(rfm_table[['고객ID', '고객분류']], on='고객ID', how='left')

# 각 세그먼트별 고객 수 시각화
plt.figure(figsize=(12, 6))
sns.countplot(y='고객분류', data=customer_info, order=customer_info['고객분류'].value_counts().index)
plt.title('Customer Distribution by RFM Segments')
plt.xlabel('고객 수')
plt.ylabel('RFM Segment')
plt.show()

# RFM Score 분포 시각화
plt.figure(figsize=(12, 6))
sns.histplot(rfm_table['RFM_Score'], bins=20, kde=True)
plt.title('RFM Score Distribution')
plt.xlabel('RFM Score')
plt.ylabel('Frequency')
plt.show()

print(customer_info)