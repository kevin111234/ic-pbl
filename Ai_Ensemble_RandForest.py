from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from matplotlib import font_manager, rc
from matplotlib import pyplot as plt
import pandas as pd

import data_frame

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

# 데이터 로드
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer_onlinesales(sql_pswd)
customer_onlinesales_df = data_frame.customer_onlinesales_df

# 데이터 전처리
# '고객ID' 열에서 'USER_'를 제거하고 숫자 부분만 추출하여 새로운 열 생성
customer_onlinesales_df['고객ID_숫자'] = customer_onlinesales_df['고객ID'].str[5:].astype(int)
# 기존의 '고객ID' 열은 더 이상 필요하지 않으므로 삭제
customer_onlinesales_df.drop(columns=['고객ID'], inplace=True)
customer_onlinesales_df['날짜'] = pd.to_datetime(customer_onlinesales_df['날짜'])
customer_onlinesales_df.set_index('날짜', inplace=True)
customer_onlinesales_df = customer_onlinesales_df[['고객ID_숫자', '성별', '가입기간', '고객분류', '제품ID', '제품카테고리', '수량', '평균금액', '배송료', '쿠폰상태']]
customer_onlinesales_df.columns = ['고객ID_숫자', '성별', '가입기간', '고객분류', '제품ID', '제품카테고리', '수량', '평균금액', '배송료', '쿠폰상태']
customer_onlinesales_df = customer_onlinesales_df.dropna()

# 데이터프레임 출력
print(customer_onlinesales_df)

X = customer_onlinesales_df[['고객ID_숫자','성별','가입기간','고객분류','제품카테고리','쿠폰상태']]
y = customer_onlinesales_df['수량']

# 훈련 데이터와 테스트 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# CatBoost 모델 생성 및 훈련
model = CatBoostRegressor(iterations=100, learning_rate=0.1, depth=6, loss_function='RMSE', random_seed=42)
model.fit(X_train, y_train, eval_set=(X_test, y_test), verbose=10, plot=True)

# 테스트 데이터에 대한 예측
y_pred = model.predict(X_test)

# 성능 평가
mse = mean_squared_error(y_test, y_pred)
print("MSE:", mse)

# 예측 결과 시각화
plt.figure(figsize=(10, 6))
plt.plot(y_test, label='Actual')
plt.plot(y_pred, label='Predicted')
plt.title('Actual vs Predicted Sales Quantity')
plt.xlabel('Index')
plt.ylabel('Sales Quantity')
plt.legend()
plt.show()
