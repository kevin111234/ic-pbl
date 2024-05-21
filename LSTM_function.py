import numpy as np
from keras import Sequential
from keras import layers, models
from keras import preprocessing
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
import sqlalchemy as sa
import data_frame

# 데이터 전처리 함수
def data_preprocessing():
    print("data is preprocessing")
    X = 0
    y = 0
    vocab_size = 0
    max_length = 0
    return X, y, vocab_size, max_length

# LSTM 모델 구축
def LSTM_model(X, y, vocab_size=None, max_length=None):
    model = Sequential()
    if len(X.shape) == 2: #시계열 데이터인 경우
        model.add(layers.LSTM(50, activation='relu', input_shape=(X.shape[1], 1)))
    else: # 텍스트 데이터인 경우
        model.add(layers.Embedding(input_dim=vocab_size, output_dim=50, input_length=max_length))
        model.add(layers.LSTM(50, activation='relu'))
    return model


def model_predictions(model):
    predictions = model.predict()
    return predictions

def model_save(model, model_name):
    model.save(f"models/{model_name}.h5")

def model_import(model_name):
    loaded_model = models.load_model(f"{model_name}.h5")
    return loaded_model