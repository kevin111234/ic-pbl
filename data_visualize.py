import pandas as pd
from sqlalchemy import create_engine
import pymysql
from matplotlib import pyplot as plt
from matplotlib import font_manager, rc
import numpy as np
from sklearn.manifold import TSNE
import seaborn as sns

import data_output

# 한글 폰트 경로 설정
font_path = "GmarketSansTTFMedium.ttf"  # 사용하고자 하는 한글 폰트 경로로 변경
# 폰트 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams.update({'font.size': 10})

sql_pswd = input("SQL 비밀번호를 입력해주세요: ")

# 데이터프레임 불러오기
engine,query = data_output.db_pull_out("*","customer_info", sql_pswd)
customer_df = pd.read_sql(query, engine)
engine,query = data_output.db_pull_out("*","discount_info", sql_pswd)
discount_df = pd.read_sql(query, engine)
engine,query = data_output.db_pull_out("*","marketing_info", sql_pswd)
marketing_df = pd.read_sql(query, engine)
engine,query = data_output.db_pull_out("*","onlinesales_info", sql_pswd)
onlisesales_df = pd.read_sql(query, engine)


# 카테고리 목록, 지역 목록
categories = ["Nest-USA","Office","Apparel","Drinkware","Notebooks & Journals","Waze","Fun","Headgear","Lifestyle","Nest-Canada","Bags",
                "Gift Cards","Android","Bottles","Backpacks","Google","Housewares","Accessories","Nest","More Bags"]
regions = ["Chicago", "California", "NewYork", "New Jersey", "Washington DC"]

# 1.지역별 선호제품 경향 파악
# 동적 SQL 쿼리 생성
query = """SELECT customer_info.고객지역, {}
FROM customer_info JOIN onlinesales_info ON customer_info.고객ID=onlinesales_info.고객ID
GROUP BY customer_info.고객지역;
"""
# 각 카테고리에 대한 CASE 문 생성
case_statements = ",\n".join([f"(SUM(CASE WHEN 제품카테고리 = '{category}' THEN 1 ELSE 0 END)/COUNT(*))*100 AS '{category.lower()}비율'" for category in categories])
# 쿼리 문자열에 CASE 문 삽입
query = query.format(case_statements)
local_count_df = pd.read_sql(query, engine)

# 2. 성별에 따른 시장규모 비교
engine,query = data_output.db_group_1column("customer_info.성별, COUNT(DISTINCT customer_info.고객ID)AS 고객_수, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.성별 ORDER BY 구매금액 DESC")
gender_df = pd.read_sql(query, engine)

# 3. 가입기간별 구입추이 경향 파악
# 가입기간별 카테고리 구매정보
engine,query = data_output.db_group_1column("customer_info.가입기간, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY customer_info.가입기간 ORDER BY 가입기간 ASC")
period_customer_df = pd.read_sql(query, engine)

# 4. 성별에 따른 카테고리별 (평균) 구매량 비교
engine,query = data_output.db_group_1column("customer_info.`성별`, onlinesales_info.`제품카테고리`,COUNT(DISTINCT customer_info.고객ID)AS 고객수, SUM(onlinesales_info.`수량`)AS 수량, SUM(평균금액*수량+배송료)AS 구매금액, (SUM(onlinesales_info.`수량`)/COUNT(*))AS 평균수량,(SUM(평균금액*수량+배송료)/COUNT(*))AS 평균구매액"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,'''WHERE 성별="남"GROUP BY customer_info.`성별`, onlinesales_info.`제품카테고리`''')
male_customer_df = pd.read_sql(query, engine)
engine,query = data_output.db_group_1column("customer_info.`성별`, onlinesales_info.`제품카테고리`,COUNT(DISTINCT customer_info.고객ID)AS 고객수, SUM(onlinesales_info.`수량`)AS 수량, SUM(평균금액*수량+배송료)AS 구매금액, (SUM(onlinesales_info.`수량`)/COUNT(*))AS 평균수량,(SUM(평균금액*수량+배송료)/COUNT(*))AS 평균구매액"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,'''WHERE 성별="여"GROUP BY customer_info.`성별`, onlinesales_info.`제품카테고리`''')
female_customer_df = pd.read_sql(query, engine)

# 5. 카테고리별 시장규모 비교
engine,query = data_output.db_group_1column("onlinesales_info.`제품카테고리`,COUNT(DISTINCT customer_info.고객ID)AS 고객수, SUM(onlinesales_info.`수량`)AS 수량, SUM(평균금액*수량+배송료)AS 구매금액, (SUM(onlinesales_info.`수량`)/COUNT(*))AS 평균수량,(SUM(평균금액*수량+배송료)/COUNT(*))AS 평균구매액"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY onlinesales_info.`제품카테고리`")
category_df = pd.read_sql(query, engine)

# 6. 월별 구매량 비교
# 개별 월별 구매량
engine,query = data_output.db_group_1column("onlinesales_info.월, COUNT(DISTINCT customer_info.고객ID)AS 고객수, SUM(평균금액*수량+배송료)AS 구매금액, SUM(수량)AS 수량"
                                            ,"customer_info", "onlinesales_info", "고객ID", sql_pswd
                                            ,"GROUP BY onlinesales_info.월 ORDER BY 월 ASC")
month_customer_df = pd.read_sql(query, engine)

# 고객정보 판매정보 결합 - 고객특성 분석
engine,query = data_output.db_group_1column("*","customer_info", "onlinesales_info", "고객ID", sql_pswd)
customer_onlinesales_df = pd.read_sql(query, engine)
customer_onlinesales_df = pd.get_dummies(customer_onlinesales_df, columns=['고객지역'])

# 할인율별 구매정보 + 카테고리
engine,query = data_output.db_group_2column("""onlinesales_info.제품카테고리, 
    discount_info.`할인율`, 
    SUM(onlinesales_info.수량) AS 수량, 
    SUM(onlinesales_info.평균금액 * onlinesales_info.수량 + onlinesales_info.배송료) AS 구매금액,
    SUM(CASE WHEN onlinesales_info.쿠폰상태 = 'used' THEN onlinesales_info.수량 ELSE 0 END) AS used_count,
    SUM(CASE WHEN onlinesales_info.쿠폰상태 = 'not used' THEN onlinesales_info.수량 ELSE 0 END) AS not_used_count,
    SUM(CASE WHEN onlinesales_info.쿠폰상태 = 'clicked' THEN onlinesales_info.수량 ELSE 0 END) AS clicked_count,
    SUM(onlinesales_info.수량) AS total_count,
    SUM(CASE WHEN onlinesales_info.쿠폰상태 = 'used' THEN onlinesales_info.수량 ELSE 0 END) / SUM(onlinesales_info.수량) AS used_ratio,
    SUM(CASE WHEN onlinesales_info.쿠폰상태 = 'not used' THEN onlinesales_info.수량 ELSE 0 END) / SUM(onlinesales_info.수량) AS not_used_ratio,
    SUM(CASE WHEN onlinesales_info.쿠폰상태 = 'clicked' THEN onlinesales_info.수량 ELSE 0 END) / SUM(onlinesales_info.수량) AS clicked_ratio"""
                                            , "discount_info","onlinesales_info","월","제품카테고리", sql_pswd
                                            ,"GROUP BY onlinesales_info.제품카테고리, discount_info.`할인율`")
rate_discount_df = pd.read_sql(query, engine)

# 마케팅정보 판매정보 결합
engine,query = data_output.db_group_1column("marketing_info.날짜, 오프라인비용, 온라인비용, SUM(수량)AS 수량, SUM(평균금액*수량+배송료)AS 구매금액",
                                            "marketing_info", "onlinesales_info", "날짜", sql_pswd, "GROUP BY 날짜")
marketing_onlinesales_df = pd.read_sql(query, engine)

# 분석 결과 시각화

# 첫번째 창
# 고객 지역별 상품 구매 비율, 성별에 따른 구매금액, 가입기간별 구매금액 및 구매 수량 그래프를 배치
fig, axes = plt.subplots(2, 2, figsize=(15, 18), gridspec_kw={'height_ratios': [2, 2]}) 

# 첫 번째 서브플롯: 고객 지역별 상품 구매 비율
for i, region in enumerate(regions):
    x = np.arange(len(categories))  # x축에 사용할 카테고리 인덱스
    y = local_count_df[[f"{category.lower()}비율" for category in categories]].loc[i]  # 해당 지역의 카테고리별 비율
    axes[0, 0].plot(x, y, label=region)

axes[0, 0].set_xticks(np.arange(len(categories)))  # x축 눈금 설정
axes[0, 0].set_xticklabels(categories, rotation=90)  # x축 눈금 라벨 설정
axes[0, 0].set_xlabel("카테고리")
axes[0, 0].set_ylabel("상품 구매 비율")
axes[0, 0].set_title("고객 지역별 상품 구매 비율")
axes[0, 0].legend()

# 두 번째 서브플롯: 성별에 따른 구매금액
axes[0, 1].bar(gender_df["성별"], gender_df["구매금액"], color="skyblue", width=0.4)
axes[0, 1].set_xlabel("성별")
axes[0, 1].set_ylabel("구매금액")
axes[0, 1].set_title("성별에 따른 구매금액 (단위: 억 원)")
for i, value in enumerate(gender_df["구매금액"]):
    axes[0, 1].text(i, value + 1, str(round(value/1000000000, 3)), ha='center')

# 세 번째 서브플롯: 가입기간별 구매금액
axes[1, 0].plot(period_customer_df["가입기간"], period_customer_df["구매금액"], color="blue")
axes[1, 0].set_xlabel("가입기간")
axes[1, 0].set_ylabel("구매금액")
axes[1, 0].set_title("가입기간별 구매금액")

# 네 번째 서브플롯: 가입기간별 구매 수량
axes[1, 1].plot(period_customer_df["가입기간"], period_customer_df["수량"], color="green")
axes[1, 1].set_xlabel("가입기간")
axes[1, 1].set_ylabel("구매 수량")
axes[1, 1].set_title("가입기간별 구매 수량")

plt.tight_layout()  # 서브플롯 간 간격 조절
plt.show()


# 두번째 창
# 성별에 따른 구매 수량, 구매금액, 평균 수량 및 평균 구매 금액을 나타내는 그래프를 배치
# 성별에 따른 평균 구매 수량
categories = male_customer_df["제품카테고리"]

# 그래프를 위한 데이터 준비
quantity_male = male_customer_df["수량"]
quantity_female = female_customer_df["수량"]
purchase_amount_male = male_customer_df["구매금액"]
purchase_amount_female = female_customer_df["구매금액"]
average_quantity_male = male_customer_df["평균수량"]
average_quantity_female = female_customer_df["평균수량"]
average_purchase_amount_male = male_customer_df["평균구매액"]
average_purchase_amount_female = female_customer_df["평균구매액"]

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

# 데이터프레임을 할인율에 따라 정렬
rate_discount_df.sort_values(by='할인율', inplace=True)

# 제품 카테고리 리스트
categories = rate_discount_df['제품카테고리'].unique()

# 할인율 리스트
discount_rates = rate_discount_df['할인율'].unique()

# 그래프를 그릴 때 사용할 색상
colors = sns.color_palette("husl", 3)

# 그래프의 각 카테고리별 비율을 누적하여 저장할 리스트
used_ratio_cumulative = [0] * len(categories)
not_used_ratio_cumulative = [0] * len(categories)
clicked_ratio_cumulative = [0] * len(categories)

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 수량 그래프
axes[0, 0].bar(category_df["제품카테고리"], category_df["수량"], color="skyblue")
axes[0, 0].set_ylabel("수량")
axes[0, 0].set_title("카테고리별 구매 수량")
axes[0, 0].tick_params(axis='x', labelrotation=90)

# 구매금액 그래프
axes[0, 1].bar(category_df["제품카테고리"], category_df["구매금액"], color="salmon")
axes[0, 1].set_ylabel("구매금액")
axes[0, 1].set_title("카테고리별 구매금액")
axes[0, 1].tick_params(axis='x', labelrotation=90)

# 평균수량 그래프
axes[1, 0].bar(category_df["제품카테고리"], category_df["평균수량"], color="lightgreen")
axes[1, 0].set_ylabel("평균수량")
axes[1, 0].set_title("카테고리별 평균 구매 수량")
axes[1, 0].tick_params(axis='x', labelrotation=90)

# 평균구매액 그래프
axes[1, 1].bar(category_df["제품카테고리"], category_df["평균구매액"], color="orange")
axes[1, 1].set_ylabel("평균구매액")
axes[1, 1].set_title("카테고리별 평균 구매금액")
axes[1, 1].tick_params(axis='x', labelrotation=90)

plt.tight_layout()
plt.show()

# 할인율에 따른 구매량 시각화
plt.figure(figsize=(10, 6))
sns.barplot(x="할인율", y="수량", hue="제품카테고리", data=rate_discount_df)
plt.title('카테고리별 할인율에 따른 구매량')
plt.xlabel('할인율')
plt.ylabel('구매량')
plt.legend(title='제품카테고리')
plt.xticks()
plt.show()

# 카테고리별 할인율에 따른 누적 비중과 구매금액에 따른 비율
plt.figure(figsize=(12, 8))
for i, rate in enumerate(discount_rates):
    data = rate_discount_df[rate_discount_df['할인율'] == rate]
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
axes[0, 0].bar(marketing_onlinesales_df.index, marketing_onlinesales_df['오프라인비용'], label='오프라인비용')
axes[0, 0].set_title('매일의 오프라인 비용')
axes[0, 0].set_xlabel('날짜')
axes[0, 0].set_ylabel('오프라인비용')
axes[0, 0].legend()
axes[0, 0].grid(True)
axes[0, 0].tick_params(axis='x', rotation=45)

# 매일의 온라인 마케팅 비용
axes[0, 1].bar(marketing_onlinesales_df.index, marketing_onlinesales_df['온라인비용'], label='온라인 마케팅 비용', color='tab:purple')
axes[0, 1].set_title('매일의 온라인 마케팅 비용')
axes[0, 1].set_xlabel('날짜')
axes[0, 1].set_ylabel('온라인비용')
axes[0, 1].legend()
axes[0, 1].grid(True)
axes[0, 1].tick_params(axis='x', rotation=45)

# 매일의 수량
axes[1, 0].bar(marketing_onlinesales_df.index, marketing_onlinesales_df['수량'], label='수량', color='tab:orange')
axes[1, 0].set_title('매일의 수량')
axes[1, 0].set_xlabel('날짜')
axes[1, 0].set_ylabel('수량')
axes[1, 0].legend()
axes[1, 0].grid(True)
axes[1, 0].tick_params(axis='x', rotation=45)

# 매일의 구매금액
axes[1, 1].bar(marketing_onlinesales_df.index, marketing_onlinesales_df['구매금액'], label='구매금액', color='tab:blue')
axes[1, 1].set_title('매일의 구매금액')
axes[1, 1].set_xlabel('날짜')
axes[1, 1].set_ylabel('구매금액')
axes[1, 1].legend()
axes[1, 1].grid(True)
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()