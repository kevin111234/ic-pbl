import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import confusion_matrix
import tensorflow as tf
import keras
import matplotlib.pyplot as plt
import seaborn as sns

import data_frame

# 데이터 로드 및 준비
# 이 부분은 실제 데이터 로드 방식에 맞게 조정하세요.
data_frame.all_data()
RFM_df = data_frame.customer_onlinesales_all_df
RFM_df["날짜"] = pd.to_datetime(RFM_df['날짜'])

# Recency 계산
today_date = RFM_df['날짜'].max() + pd.Timedelta(days=1)
RFM_df['Recency'] = (today_date - RFM_df['날짜']).dt.days

# Frequency 계산
RFM_df['Frequency'] = RFM_df.groupby(['고객ID', '제품카테고리'])['날짜'].transform('count')

# Monetary 계산
RFM_df['Monetary'] = RFM_df.groupby(['고객ID', '제품카테고리'])['구매금액'].transform('sum')

# 카테고리별 RFM 분석 결과
category_rfm = RFM_df[['고객ID', '제품카테고리', 'Recency', 'Frequency', 'Monetary']].drop_duplicates()

# '성별'과 '고객지역' 컬럼 추가
customer_info = RFM_df[['고객ID', '성별', '고객지역']].drop_duplicates()
category_rfm = category_rfm.merge(customer_info, on='고객ID', how='left')

# 라벨 인코딩 (카테고리 및 성별 등)
label_encoders = {}
for column in ['제품카테고리', '성별', '고객지역']:
    label_encoders[column] = LabelEncoder()
    category_rfm[column] = label_encoders[column].fit_transform(category_rfm[column])

# RFM 점수 계산 (임의로 예시)
category_rfm['R_Score'] = pd.qcut(category_rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
category_rfm['F_Score'] = pd.qcut(category_rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
category_rfm['M_Score'] = pd.qcut(category_rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
category_rfm['RFM_Score'] = category_rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

# 특성과 타겟 분리
features = ['제품카테고리', 'Recency', 'Frequency', 'Monetary', '성별', '고객지역']
X = category_rfm[features].values
y = category_rfm['RFM_Score'].values

# 데이터 스케일링
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 타겟 원핫 인코딩
y_encoded = keras.utils.to_categorical(y)

# 데이터셋 분할
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# 모델 구축
model = keras.models.Sequential()
model.add(keras.layers.Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(32, activation='relu'))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(y_train.shape[1], activation='softmax'))

# 모델 컴파일
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 모델 학습
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

# 모델 평가
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Test Accuracy: {accuracy}')

# 예측 수행
y_pred = model.predict(X_test)

# 예측 결과 및 실제 결과 준비
y_test_labels = np.argmax(y_test, axis=1)
y_pred_labels = np.argmax(y_pred, axis=1)

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# 혼동 행렬
sns.heatmap(confusion_matrix(y_test_labels, y_pred_labels), annot=True, fmt='d', cmap='Blues', ax=axes[0])
axes[0].set_xlabel('Predicted')
axes[0].set_ylabel('Actual')
axes[0].set_title('Confusion Matrix')

# 분포 그래프
comparison_df = pd.DataFrame({'Actual': y_test_labels, 'Predicted': y_pred_labels})
sns.countplot(x='Actual', data=comparison_df, hue='Actual', palette='viridis', ax=axes[1], legend=False)
axes[1].set_title('Distribution of Actual RFM Scores')
plt.tight_layout()
plt.show()