import numpy as np
import keras
from keras import Sequential
from keras import layers
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
import sqlalchemy as sa
import data_frame
import LSTM_data

sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.all_data(sql_pswd)

# LSTM 모델 생성 함수
def create_model(input_length, vocab_size, embedding_dim=50, lstm_units=50, dropout_rate=0.2):
    model = Sequential()
    model.add(layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=input_length))
    model.add(layers.LSTM(lstm_units, activation='relu'))
    model.add(layers.Dropout(dropout_rate))  # Dropout 추가
    model.add(layers.Dense(vocab_size, activation='softmax'))

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# 학습 함수
def train_model(model, X_train, y_train, X_val, y_val, epochs=10, batch_size=32):
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val, y_val))
    return history

# 예측 함수
def make_predictions(model, X, item_encoder):
    predictions = model.predict(X)
    predicted_indices = np.argmax(predictions, axis=1)
    return item_encoder.inverse_transform(predicted_indices)

# 전체 파이프라인 형성
def run_lstm_analysis(user_ids, item_ids, purchases, test_size=0.2, epochs=10, batch_size=32):
    # 데이터 전처리
    X, y, vocab_size, max_sequence_length = LSTM_data.preprocess_data(user_ids, item_ids, purchases)
    
    # Train-test split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # 모델 생성
    model = create_model(input_length=max_sequence_length, vocab_size=vocab_size)
    
    # 모델 학습
    history = train_model(model, X_train, y_train, X_val, y_val, epochs=epochs, batch_size=batch_size)
    
    # 예측
    predictions = make_predictions(model, X_val, LabelEncoder().fit(item_ids))
    
    return model, history, predictions


# 예시 데이터 (사용자 ID, 상품 ID, 구매 시퀀스)
user_ids = np.array([1, 2, 3])
item_ids = np.array([101, 102, 103, 104, 105])
purchases = [
    [101, 102, 103],
    [102, 104],
    [101, 105, 103]
]
model, history, predictions = run_lstm_analysis(user_ids, item_ids, purchases)

# 결과 출력
print("Predictions:", predictions)

