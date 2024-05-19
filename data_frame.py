import pandas as pd
from sqlalchemy import create_engine
import pymysql
import seaborn as sns

import data_output

def all_data(sql_pswd):

    global customer_df # 소비자정보 기본 데이터
    global marketing_df # 마케팅정보 기본데이터
    global discount_df # 할인정보 기본데이터
    global onlisesales_df # 온라인판매정보 기본데이터
    global categories # 제품카테고리 목록
    global regions # 고객지역 목록
    global local_count_df # 고객지역별 제품카테고리별 구매비율 데이터
    global gender_df # 성별에 따른 고객 수, 구매금액 및 수량 총계
    global period_customer_df # 가입기간에 따른 구매금액 및 수량
    global male_customer_df # 남성의 제품 카테고리별 구매 데이터
    global female_customer_df # 여성의 제품 카테고리별 구매 데이터
    global category_df # 제품카테고리별 구매 데이터
    global month_customer_df # 월별 구매 데이터
    global customer_onlinesales_df # 고객지역별 구매 데이터(고객지역 데이터 변화)
    global rate_discount_df # 제품카테고리별 할인율에 따른 쿠폰사용 비율
    global marketing_onlinesales_df # 마케팅비용 대비 구매 데이터
    global customer_onlinesales_all_df # 고객 구매정보 종합 데이터

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
    engine,query = data_output.db_group_1column("customer_info.가입기간, SUM(평균금액*수량+배송료)/COUNT(*)AS 구매금액, SUM(수량)/COUNT(*)AS 수량"
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

    # 고객정보 판매정보 결합
    engine,query = data_output.db_group_1column("customer_info.고객ID, 성별, 고객지역, 날짜, 제품카테고리, (평균금액*수량+배송료)AS 구매금액",
                                                "customer_info", "onlinesales_info", "고객ID", sql_pswd)
    customer_onlinesales_all_df = pd.read_sql(query, engine)