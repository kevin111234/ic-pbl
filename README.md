# ic-pbl
대회용 데이터분석 툴

## Artificial_Neuron.py
RFM 분석방법을 활용하여 분석한 결과를 바탕으로 RFM 점수 예측하기

## RFM_analyze.py
RFM 분석방법을 활용하여 점수를 매기고 이를 바탕으로 고객 그룹을 10개로 나눔.

## data_visualize.py
sql에서 데이터를 받아와서 이리저리 조합하고 시각화하는 기능까지 구현완료.

## data_analyze.py
csv 파일을 읽고 정리해서 sql에 저장하는 기능까지 구현 완료.

## data_save.py
sql 쿼리와 데이터베이스에 저장하는 함수까지 구현완료.

## data_read.py
로우데이터 csv 파일을 읽고 클랜징하는 함수 구현완료.

## data_predict.py
데이터 분석해서 예측하는 기능

## data_frame.py
데이터프레임으로 데이터 다 가져와주는 함수
- customer_df # 소비자정보 기본 데이터
- marketing_df # 마케팅정보 기본데이터
- discount_df # 할인정보 기본데이터
- onlisesales_df # 온라인판매정보 기본데이터
- categories # 제품카테고리 목록
- regions # 고객지역 목록
- local_count_df # 고객지역별 제품카테고리별 구매비율 데이터
- gender_df # 성별에 따른 고객 수, 구매금액 및 수량 총계
- period_customer_df # 가입기간에 따른 구매금액 및 수량
- male_customer_df # 남성의 제품 카테고리별 구매 데이터
- female_customer_df # 여성의 제품 카테고리별 구매 데이터
- category_df # 제품카테고리별 구매 데이터
- month_customer_df # 월별 구매 데이터
- customer_onlinesales_df # 고객지역별 구매 데이터(고객지역 데이터 변화)
- rate_discount_df # 제품카테고리별 할인율에 따른 쿠폰사용 비율
- marketing_onlinesales_df # 마케팅비용 대비 구매 데이터