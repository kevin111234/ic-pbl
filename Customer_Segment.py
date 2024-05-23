import data_frame
import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pmdarima as pm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

# 기본 데이터 로드
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer(sql_pswd)
data_frame.marketing(sql_pswd)
data_frame.discount(sql_pswd)
data_frame.onlinesales(sql_pswd)
customer_df = data_frame.customer_df
marketing_df = data_frame.marketing_df
discount_df = data_frame.discount_df
onlinesales_df = data_frame.onlinesales_df

# 데이터 전처리
# ID 형식들 숫자로 변환
customer_df['고객ID'] = customer_df['고객ID'].astype(str).str[5:]
customer_df['고객ID'] = customer_df['고객ID'].astype(int)
onlinesales_df['고객ID'] = onlinesales_df['고객ID'].astype(str).str[5:]
onlinesales_df['고객ID'] = onlinesales_df['고객ID'].astype(int)
onlinesales_df['제품ID'] = onlinesales_df['제품ID'].astype(str).str[8:]
onlinesales_df['거래ID'] = onlinesales_df['거래ID'].astype(str).str[12:]
onlinesales_df['거래ID'] = onlinesales_df['거래ID'].astype(int)

# 제품ID랑 카테고리 연결
# onlinesales_df['제품ID'] = onlinesales_df['제품카테고리'] + " " + onlinesales_df['제품ID']

# 제품카테고리에서 중복 제거
unique_categories = onlinesales_df['제품카테고리'].drop_duplicates()
unique_locations = customer_df['고객지역'].drop_duplicates()

# 텍스트 데이터 벡터로 변환 (제품카테고리, 고객지역)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_word_embedding(word):
    # BERT 입력 형식으로 변환
    inputs = tokenizer(word, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    # CLS 토큰의 임베딩을 사용
    embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    return embedding

# 중복 제거된 제품카테고리에 대해 임베딩 생성
unique_categories_df = pd.DataFrame(unique_categories, columns=['제품카테고리'])
unique_categories_df['embedding_category'] = unique_categories_df['제품카테고리'].apply(get_word_embedding)
unique_locations_df = pd.DataFrame(unique_locations, columns=['고객지역'])
unique_locations_df['embedding_location'] = unique_locations_df['고객지역'].apply(get_word_embedding)

# 임베딩 데이터프레임과 원래 데이터프레임 병합
onlinesales_df = onlinesales_df.merge(unique_categories_df, on='제품카테고리', how='left')
customer_df = customer_df.merge(unique_locations_df, on='고객지역', how='left')

# 코사인 유사도 계산
embeddings = list(unique_categories_df['embedding_category'])
cosine_sim_matrix_category = cosine_similarity(embeddings)
category_cosine_sim_df = pd.DataFrame(cosine_sim_matrix_category, index=unique_categories_df['제품카테고리'], columns=unique_categories_df['제품카테고리'])
embeddings = list(unique_locations_df['embedding_location'])
cosine_sim_matrix_location = cosine_similarity(embeddings)
location_cosine_sim_df = pd.DataFrame(cosine_sim_matrix_location, index=unique_locations_df['고객지역'], columns=unique_locations_df['고객지역'])

# 데이터 병합
customer_df['성별'] = customer_df['성별'].map({'남': 0, '여': 1})
onlinesales_df['쿠폰상태'] = onlinesales_df['쿠폰상태'].map({'Not Used': 0, 'Clicked': 1, 'Used':2})
customer_onlinesales_df = onlinesales_df.merge(customer_df, on='고객ID', how='left')

# 모델 형성

# 모델 학습


#고객 분류
# - Recency 계산: 가장 최근 구매 일자로부터 경과일 계산
customer_onlinesales_df["날짜"]= pd.to_datetime(customer_onlinesales_df['날짜'])
max_date = customer_onlinesales_df['날짜'].max()
customer_onlinesales_df['날짜'] = pd.to_datetime(customer_onlinesales_df['날짜'])
customer_onlinesales_df['최근거래일자'] = (max_date - customer_onlinesales_df['날짜']).dt.days
# - Frequency, Monetary 계산: 고객별 구매 횟수, 총 구매 금액 계산
data_frame.customer_onlinesales_category(sql_pswd)
rfm_df = data_frame.customer_onlinesales_category_df

print(rfm_df)
"""
silhouettes = []
silhouette_x = []
for k in range(2, 30):  # K 값 범위 설정 (2부터 10까지)
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(rfm_df)
    silhouettes.append(silhouette_score(rfm_df, kmeans.labels_))
    silhouette_x.append(k)
largest_number = max(silhouettes)
largest_index = silhouettes.index(largest_number)
print(largest_index)

# 고객군별 특성
    # 데이터 추출
    # 데이터 시각화"""