import pandas as pd
from sqlalchemy import create_engine
import pymysql
from matplotlib import pyplot as plt
from matplotlib import font_manager, rc
import numpy as np
from sklearn.manifold import TSNE
import seaborn as sns

import data_output
import data_frame

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer(sql_pswd)
data_frame.discount(sql_pswd)
data_frame.marketing(sql_pswd)
data_frame.onlinesales(sql_pswd)
data_frame.category_list()
data_frame.region_list()
data_frame.local_count(sql_pswd)
data_frame.gender(sql_pswd)
data_frame.period_customer(sql_pswd)
data_frame.male_customer(sql_pswd)
data_frame.female_customer(sql_pswd)
data_frame.category(sql_pswd)
data_frame.month_customer(sql_pswd)
data_frame.customer_onlinesales(sql_pswd)
data_frame.rate_discount(sql_pswd)
data_frame.marketing_onlinesales(sql_pswd)
data_frame.customer_onlinesales_all(sql_pswd)

# 분석 결과 시각화

# 첫번째 창
# 고객 지역별 상품 구매 비율, 성별에 따른 구매금액, 가입기간별 구매금액 및 구매 수량 그래프를 배치
fig, axes = plt.subplots(2, 2, figsize=(15, 18), gridspec_kw={'height_ratios': [2, 2]}) 

# 첫 번째 서브플롯: 고객 지역별 상품 구매 비율
for i, region in enumerate(data_frame.regions):
    x = np.arange(len(data_frame.categories))  # x축에 사용할 카테고리 인덱스
    y = data_frame.local_count_df[[f"{category.lower()}비율" for category in data_frame.categories]].loc[i]  # 해당 지역의 카테고리별 비율
    axes[0, 0].plot(x, y, label=region)

axes[0, 0].set_xticks(np.arange(len(data_frame.categories)))  # x축 눈금 설정
axes[0, 0].set_xticklabels(data_frame.categories, rotation=90)  # x축 눈금 라벨 설정
axes[0, 0].set_xlabel("카테고리")
axes[0, 0].set_ylabel("상품 구매 비율")
axes[0, 0].set_title("고객 지역별 상품 구매 비율")
axes[0, 0].legend()

# 두 번째 서브플롯: 성별에 따른 구매금액
axes[0, 1].bar(data_frame.gender_df["성별"], data_frame.gender_df["구매금액"], color="skyblue", width=0.4)
axes[0, 1].set_xlabel("성별")
axes[0, 1].set_ylabel("구매금액")
axes[0, 1].set_title("성별에 따른 구매금액 (단위: 억 원)")
for i, value in enumerate(data_frame.gender_df["구매금액"]):
    axes[0, 1].text(i, value + 1, str(round(value/1000000000, 3)), ha='center')

# 세 번째 서브플롯: 가입기간별 구매금액
axes[1, 0].plot(data_frame.period_customer_df["가입기간"], data_frame.period_customer_df["구매금액"], color="blue")
axes[1, 0].set_xlabel("가입기간")
axes[1, 0].set_ylabel("구매금액")
axes[1, 0].set_title("가입기간별 평균 구매금액")

# 네 번째 서브플롯: 가입기간별 구매 수량
axes[1, 1].plot(data_frame.period_customer_df["가입기간"], data_frame.period_customer_df["수량"], color="green")
axes[1, 1].set_xlabel("가입기간")
axes[1, 1].set_ylabel("구매 수량")
axes[1, 1].set_title("가입기간별 평균 구매 수량")

plt.tight_layout()  # 서브플롯 간 간격 조절
plt.show()


# 두번째 창
# 성별에 따른 구매 수량, 구매금액, 평균 수량 및 평균 구매 금액을 나타내는 그래프를 배치
# 성별에 따른 평균 구매 수량
categories = data_frame.male_customer_df["제품카테고리"]

# 그래프를 위한 데이터 준비
quantity_male = data_frame.male_customer_df["수량"]
quantity_female = data_frame.female_customer_df["수량"]
purchase_amount_male = data_frame.male_customer_df["구매금액"]
purchase_amount_female = data_frame.female_customer_df["구매금액"]
average_quantity_male = data_frame.male_customer_df["평균수량"]
average_quantity_female = data_frame.female_customer_df["평균수량"]
average_purchase_amount_male = data_frame.male_customer_df["평균구매액"]
average_purchase_amount_female = data_frame.female_customer_df["평균구매액"]

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 수량 그래프
axes[0, 0].bar(categories, quantity_male, label="Male", color="blue", alpha=0.5)
axes[0, 0].bar(categories, quantity_female, label="Female", color="pink", alpha=0.5)
axes[0, 0].set_title("카테고리별 구매량")
axes[0, 0].set_ylabel("구매량")
axes[0, 0].legend()
axes[0, 0].tick_params(axis='x', rotation=90)  # x축 라벨 90도 회전

# 구매금액 그래프
axes[0, 1].bar(categories, purchase_amount_male, label="Male", color="blue", alpha=0.5)
axes[0, 1].bar(categories, purchase_amount_female, label="Female", color="pink", alpha=0.5)
axes[0, 1].set_title("카테고리별 구매금액")
axes[0, 1].set_ylabel("구매금액")
axes[0, 1].legend()
axes[0, 1].tick_params(axis='x', rotation=90)  # x축 라벨 90도 회전

# 평균수량 그래프
axes[1, 0].bar(categories, average_quantity_male, label="Male", color="blue", alpha=0.5)
axes[1, 0].bar(categories, average_quantity_female, label="Female", color="pink", alpha=0.5)
axes[1, 0].set_title("고객별 평균 구매 수량")
axes[1, 0].set_ylabel("평균 구매 수량")
axes[1, 0].legend()
axes[1, 0].tick_params(axis='x', rotation=90)  # x축 라벨 90도 회전

# 평균구매액 그래프
axes[1, 1].bar(categories, average_purchase_amount_male, label="Male", color="blue", alpha=0.5)
axes[1, 1].bar(categories, average_purchase_amount_female, label="Female", color="pink", alpha=0.5)
axes[1, 1].set_title("고객별 평균 구매 금액")
axes[1, 1].set_ylabel("평균 구매")
axes[1, 1].legend()
axes[1, 1].tick_params(axis='x', rotation=90)  # x축 라벨 90도 회전

plt.tight_layout()
plt.show()




# 세번째 창
# 카테고리별 시장규모, 월별 판매량, 할인율에 따른 구매량 및 마케팅 비용 분석을 나타내는 그래프를 배치
# 월별 판매량(수량)
sns.set_palette("husl")
plt.figure(figsize=(20, 12))

plt.subplot(2, 2, 1)
plt.plot(data_frame.month_customer_df.index+1, data_frame.month_customer_df['수량'], marker='o', linestyle='-', color='tab:blue')
plt.title('월별 구매량 추이')
plt.xlabel('월')
plt.ylabel('구매량')
plt.xticks(data_frame.month_customer_df.index+1)  # x 축에 월 표시
plt.grid(True)

# 월별 판매량(금액)
plt.subplot(2, 2, 2)
plt.plot(data_frame.month_customer_df.index+1, data_frame.month_customer_df['구매금액'], marker='o', linestyle='-', color='tab:orange')
plt.title('월별 구매금액 추이')
plt.xlabel('월')
plt.ylabel('구매금액')
plt.xticks(data_frame.month_customer_df.index+1)  # x 축에 월 표시
plt.grid(True)

# 월별 판매량(이용 고객 수)
plt.subplot(2, 2, 3)
plt.plot(data_frame.month_customer_df.index+1, data_frame.month_customer_df['고객수'], marker='o', linestyle='-', color='tab:green')
plt.title('월별 이용자 추이')
plt.xlabel('월')
plt.ylabel('고객수')
plt.xticks(data_frame.month_customer_df.index+1)  # x 축에 월 표시
plt.grid(True)

# 각 도시에 대한 고객 분포 시각화
customer_location_df = data_frame.customer_onlinesales_df[['고객지역_California', '고객지역_Chicago', '고객지역_New Jersey', '고객지역_New York', '고객지역_Washington DC']]
plt.subplot(2, 2, 4)
customer_location_df.sum().plot(kind='bar')
plt.title('고객 지역별 분포')
plt.xlabel('고객 지역')
plt.ylabel('고객 수')
plt.xticks(rotation=25)

plt.tight_layout()  # 서브플롯 간 간격 조정
plt.show()

# 데이터프레임을 할인율에 따라 정렬
data_frame.rate_discount_df.sort_values(by='할인율', inplace=True)

# 제품 카테고리 리스트
categories = data_frame.rate_discount_df['제품카테고리'].unique()

# 할인율 리스트
discount_rates = data_frame.rate_discount_df['할인율'].unique()

# 그래프를 그릴 때 사용할 색상
colors = sns.color_palette("husl", 3)

# 그래프의 각 카테고리별 비율을 누적하여 저장할 리스트
used_ratio_cumulative = [0] * len(categories)
not_used_ratio_cumulative = [0] * len(categories)
clicked_ratio_cumulative = [0] * len(categories)

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 수량 그래프
axes[0, 0].bar(data_frame.category_df["제품카테고리"], data_frame.category_df["수량"], color="skyblue")
axes[0, 0].set_ylabel("수량")
axes[0, 0].set_title("카테고리별 구매 수량")
axes[0, 0].tick_params(axis='x', labelrotation=90)

# 구매금액 그래프
axes[0, 1].bar(data_frame.category_df["제품카테고리"], data_frame.category_df["구매금액"], color="salmon")
axes[0, 1].set_ylabel("구매금액")
axes[0, 1].set_title("카테고리별 구매금액")
axes[0, 1].tick_params(axis='x', labelrotation=90)

# 평균수량 그래프
axes[1, 0].bar(data_frame.category_df["제품카테고리"], data_frame.category_df["평균수량"], color="lightgreen")
axes[1, 0].set_ylabel("평균수량")
axes[1, 0].set_title("카테고리별 평균 구매 수량")
axes[1, 0].tick_params(axis='x', labelrotation=90)

# 평균구매액 그래프
axes[1, 1].bar(data_frame.category_df["제품카테고리"], data_frame.category_df["평균구매액"], color="orange")
axes[1, 1].set_ylabel("평균구매액")
axes[1, 1].set_title("카테고리별 평균 구매금액")
axes[1, 1].tick_params(axis='x', labelrotation=90)

plt.tight_layout()
plt.show()

# 할인율에 따른 구매량 시각화
plt.figure(figsize=(10, 6))
sns.barplot(x="할인율", y="수량", hue="제품카테고리", data=data_frame.rate_discount_df)
plt.title('카테고리별 할인율에 따른 구매량')
plt.xlabel('할인율')
plt.ylabel('구매량')
plt.legend(title='제품카테고리')
plt.xticks()
plt.show()

# 카테고리별 할인율에 따른 누적 비중과 구매금액에 따른 비율
plt.figure(figsize=(12, 8))
for i, rate in enumerate(discount_rates):
    data = data_frame.rate_discount_df[data_frame.rate_discount_df['할인율'] == rate]
    used_ratio_cumulative += data['used_ratio']
    not_used_ratio_cumulative += data['not_used_ratio']
    clicked_ratio_cumulative += data['clicked_ratio']
    plt.bar(categories, used_ratio_cumulative, label='used_ratio' if i == 0 else None, color=colors[0], alpha=0.5)
    plt.bar(categories, not_used_ratio_cumulative, label='not_used_ratio' if i == 0 else None, bottom=used_ratio_cumulative, color=colors[1], alpha=0.5)
    plt.bar(categories, clicked_ratio_cumulative, label='clicked_ratio' if i == 0 else None, bottom=used_ratio_cumulative+not_used_ratio_cumulative, color=colors[2], alpha=0.5)

plt.title('제품 카테고리별 할인율에 따른 누적 비중과 구매금액에 따른 비율')
plt.xlabel('제품 카테고리')
plt.ylabel('누적 비중 / 구매금액')
plt.legend(title='비율 종류')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# 네번째 장

fig, axes = plt.subplots(2, 2, figsize=(20, 12))

# 매일의 오프라인 마케팅 비용
axes[0, 0].bar(data_frame.marketing_onlinesales_df.index, data_frame.marketing_onlinesales_df['오프라인비용'], label='오프라인비용')
axes[0, 0].set_title('오프라인 비용')
axes[0, 0].set_xlabel('날짜')
axes[0, 0].set_ylabel('오프라인비용')
axes[0, 0].legend()
axes[0, 0].grid(True)
axes[0, 0].tick_params(axis='x', rotation=45)

# 매일의 온라인 마케팅 비용
axes[0, 1].bar(data_frame.marketing_onlinesales_df.index, data_frame.marketing_onlinesales_df['온라인비용'], label='온라인비용', color='tab:purple')
axes[0, 1].set_title('온라인 비용')
axes[0, 1].set_xlabel('날짜')
axes[0, 1].set_ylabel('온라인비용')
axes[0, 1].legend()
axes[0, 1].grid(True)
axes[0, 1].tick_params(axis='x', rotation=45)

# 매일의 수량
axes[1, 0].bar(data_frame.marketing_onlinesales_df.index, data_frame.marketing_onlinesales_df['수량'], label='수량', color='tab:orange')
axes[1, 0].set_title('판매 수량')
axes[1, 0].set_xlabel('날짜')
axes[1, 0].set_ylabel('수량')
axes[1, 0].legend()
axes[1, 0].grid(True)
axes[1, 0].tick_params(axis='x', rotation=45)

# 매일의 구매금액
axes[1, 1].bar(data_frame.marketing_onlinesales_df.index, data_frame.marketing_onlinesales_df['구매금액'], label='금액', color='tab:blue')
axes[1, 1].set_title('판매 금액')
axes[1, 1].set_xlabel('날짜')
axes[1, 1].set_ylabel('구매금액')
axes[1, 1].legend()
axes[1, 1].grid(True)
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

# 물가상승정도 확인하기
data_frame.onlinesales_df['단위수량당배송료'] = data_frame.onlinesales_df['배송료'] / data_frame.onlinesales_df['수량']

earliest_latest_df = data_frame.onlinesales_df.sort_values(by='날짜').groupby('제품ID').agg({
    '평균금액': ['first', 'last'],
    '단위수량당배송료': ['first', 'last'],
    '날짜': ['first', 'last']
}).reset_index()

# 컬럼 이름 정리
earliest_latest_df.columns = ['제품ID', '초기단가', '최종단가', '초기배송료', '최종배송료', '초기날짜', '최종날짜']

# 단가 및 배송료 변동 계산
earliest_latest_df['단가변동'] = earliest_latest_df['최종단가'] - earliest_latest_df['초기단가']
earliest_latest_df['배송료변동'] = earliest_latest_df['최종배송료'] - earliest_latest_df['초기배송료']

# 구매가 한 번만 이루어진 제품 제외
filtered_df = earliest_latest_df[(earliest_latest_df['단가변동'] != 0)]

# 시각화
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

sns.barplot(x='제품ID', y='단가변동', data=earliest_latest_df, ax=axes[0], palette='viridis')
axes[0].set_title('제품ID별 단가 변동')
axes[0].set_xlabel('')
axes[0].set_xlabel('제품ID')
axes[0].set_ylabel('단가 변동')
axes[0].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

sns.barplot(x='제품ID', y='배송료변동', data=earliest_latest_df, ax=axes[1], palette='viridis')
axes[1].set_title('제품ID별 배송료 변동')
axes[0].set_xlabel('')
axes[1].set_xlabel('제품ID')
axes[1].set_ylabel('배송료 변동')
axes[1].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

plt.tight_layout()
plt.show()

# 날짜별 평균 단가 및 배송료 계산
avg_price_shipping_df = data_frame.onlinesales_df.groupby('날짜').agg({
    '평균금액': 'mean',
    '단위수량당배송료': 'mean'
}).reset_index()

# 시각화
fig, ax = plt.subplots(figsize=(14, 7))

ax.plot(avg_price_shipping_df['날짜'], avg_price_shipping_df['평균금액'], label='평균금액', color='blue')
ax.set_ylabel('평균금액', color='blue')
ax.tick_params(axis='y', labelcolor='blue')

ax2 = ax.twinx()
ax2.plot(avg_price_shipping_df['날짜'], avg_price_shipping_df['단위수량당배송료'], label='단위수량당 배송료', color='red')
ax2.set_ylabel('단위수량당 배송료', color='red')
ax2.tick_params(axis='y', labelcolor='red')

plt.title('시간변화에 따른 배송료와 상품금액 변동성')
fig.tight_layout()
plt.show()