import pandas as pd
from matplotlib import font_manager, rc
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error , mean_absolute_error
from sklearn.datasets import make_regression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import StackingRegressor

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
customer_onlinesales_df['날짜'] = pd.to_datetime(customer_onlinesales_df['날짜'])
customer_onlinesales_df.set_index('날짜', inplace=True)
customer_onlinesales_df = customer_onlinesales_df[['고객ID', '성별', '가입기간', '고객분류', '제품ID', '제품카테고리', '수량', '평균금액', '배송료', '쿠폰상태', '고객지역_California', '고객지역_Chicago',
                                                    '고객지역_New Jersey', '고객지역_New York', '고객지역_Washington DC']]
customer_onlinesales_df.columns = ['고객ID', '고객ID_x', '성별', '가입기간', '고객분류', '제품ID', '제품카테고리', '수량', '평균금액', '배송료', '쿠폰상태', '고객지역_California', '고객지역_Chicago',
                                                    '고객지역_New Jersey', '고객지역_New York', '고객지역_Washington DC']
customer_onlinesales_df = customer_onlinesales_df[['고객ID', '성별', '가입기간', '고객분류', '제품ID', '제품카테고리', '수량', '평균금액', '배송료', '쿠폰상태', '고객지역_California', '고객지역_Chicago',
                                                    '고객지역_New Jersey', '고객지역_New York', '고객지역_Washington DC']]
customer_onlinesales_df = customer_onlinesales_df.dropna()


# 원-핫 인코딩 실행 후 데이터 병합
categorical_df = customer_onlinesales_df[['성별', '제품카테고리', '고객분류', '쿠폰상태']]
encoded_df = pd.get_dummies(categorical_df)
encoded_df.index = customer_onlinesales_df.index
customer_onlinesales_df = pd.concat([customer_onlinesales_df, encoded_df], axis=1)
customer_onlinesales_df = customer_onlinesales_df.drop(columns=['성별', '제품카테고리', '고객분류', '쿠폰상태'])
# print(customer_onlinesales_df.columns)

X = customer_onlinesales_df[['가입기간', '평균금액', '배송료', '고객지역_California',
                                '고객지역_Chicago', '고객지역_New Jersey', '고객지역_New York',
                                '고객지역_Washington DC', '성별_남', '성별_여', '제품카테고리_Accessories',
                                '제품카테고리_Android', '제품카테고리_Apparel', '제품카테고리_Backpacks', '제품카테고리_Bags',
                                '제품카테고리_Bottles', '제품카테고리_Drinkware', '제품카테고리_Fun', '제품카테고리_Gift Cards',
                                '제품카테고리_Google', '제품카테고리_Headgear', '제품카테고리_Housewares',
                                '제품카테고리_Lifestyle', '제품카테고리_More Bags', '제품카테고리_Nest',
                                '제품카테고리_Nest-Canada', '제품카테고리_Nest-USA', '제품카테고리_Notebooks & Journals',
                                '제품카테고리_Office', '제품카테고리_Waze', '고객분류_곧_이탈할_고객', '고객분류_관심_필요_고객',
                                '고객분류_신규_고객', '고객분류_유망_고객', '고객분류_이탈_고객', '고객분류_잠재적_충성고객', '고객분류_챔피언',
                                '고객분류_충성_고객', '고객분류_휴면_고객', '쿠폰상태_Clicked', '쿠폰상태_Not Used',
                                '쿠폰상태_Used']]
y1 = customer_onlinesales_df['수량']
y2 = customer_onlinesales_df['평균금액']
y3 = customer_onlinesales_df['평균금액']*customer_onlinesales_df['수량']

# 훈련 데이터와 테스트 데이터로 분할
X_train, X_test, y1_train, y1_test, y2_train, y2_test, y3_train, y3_test = train_test_split(X, y1, y2, y3, test_size=0.2, random_state=42)

# 기본 모델 정의
base_models = [
    ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
    ('lr', make_pipeline(StandardScaler(), LinearRegression()))
]

# 스태킹 앙상블 모델 정의
stacking_regressor = StackingRegressor(estimators=base_models, final_estimator=LinearRegression())

# 모델 훈련 - 첫 번째 타겟 변수(수량)
stacking_regressor.fit(X_train, y1_train)

# 테스트 데이터에 대한 예측
y1_pred = stacking_regressor.predict(X_test)

# 모델 훈련 - 두 번째 타겟 변수(평균금액)
stacking_regressor.fit(X_train, y2_train)

# 테스트 데이터에 대한 예측
y2_pred = stacking_regressor.predict(X_test)

# 모델 훈련 - 세 번째 타겟 변수(제품카테고리)
stacking_regressor.fit(X_train, y3_train)

# 테스트 데이터에 대한 예측
y3_pred = stacking_regressor.predict(X_test)

# 성능 평가
mse1 = mean_squared_error(y1_test, y1_pred)
mse2 = mean_squared_error(y2_test, y2_pred)
mse3 = mean_squared_error(y3_test, y3_pred)
mae1 = mean_absolute_error(y1_test, y1_pred)
mae2 = mean_absolute_error(y2_test, y2_pred)
mae3 = mean_absolute_error(y3_test, y3_pred)
print("MSE (수량):", mse1, "MAE (수량):", mae1)
print("MSE (평균금액):", mse2, "MAE (평균금액):", mae2)
print("MSE (판매금액):", mse3, "MAE (판매금액):", mae3)

plt.figure(figsize=(12, 6))

# 수량에 대한 예측 결과 시각화
plt.subplot(1, 2, 1)
plt.scatter(y1_test, y1_pred, alpha=0.5)
plt.plot([min(y1_test), max(y1_test)], [min(y1_test), max(y1_test)], 'r--', lw=2)
plt.xlabel('Actual Quantity')
plt.ylabel('Predicted Quantity')
plt.title('Actual vs. Predicted Quantity')

# 평균금액에 대한 예측 결과 시각화
plt.subplot(1, 2, 2)
plt.scatter(y2_test, y2_pred, alpha=0.5)
plt.plot([min(y2_test), max(y2_test)], [min(y2_test), max(y2_test)], 'r--', lw=2)
plt.xlabel('Actual Average Amount')
plt.ylabel('Predicted Average Amount')
plt.title('Actual vs. Predicted Average Amount')

plt.tight_layout()
plt.show()
