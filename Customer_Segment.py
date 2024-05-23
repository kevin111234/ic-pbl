import data_frame
import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

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
onlinesales_df['제품ID'] = onlinesales_df['제품카테고리'] + " " + onlinesales_df['제품ID']

# 제품카테고리에서 중복 제거
unique_categories = onlinesales_df['제품카테고리'].drop_duplicates()

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
unique_categories_df['embedding'] = unique_categories_df['제품카테고리'].apply(get_word_embedding)

# 임베딩 데이터프레임과 원래 데이터프레임 병합
onlinesales_df = onlinesales_df.merge(unique_categories_df, on='제품카테고리', how='left')

# 코사인 유사도 계산 (optional)
embeddings = list(unique_categories_df['embedding'])
cosine_sim_matrix = cosine_similarity(embeddings)
category_cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=unique_categories_df['제품카테고리'], columns=unique_categories_df['제품카테고리'])

# 출력 (optional)
print(cosine_sim_matrix)
print(unique_categories_df)
print(category_cosine_sim_df)
print(onlinesales_df)

#모델 형성

#모델 학습

#고객 분류

#고객군별 특성
    #데이터 추출
    #데이터 시각화