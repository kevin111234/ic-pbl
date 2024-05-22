import data_frame

#기본 데이터 로드
sql_pswd = input("SQL 비밀번호를 입력해주세요: ")
data_frame.customer(sql_pswd)
data_frame.marketing(sql_pswd)
data_frame.discount(sql_pswd)
data_frame.onlinesales(sql_pswd)
category_df = data_frame.category_df
marketing_df = data_frame.marketing_df
discount_df = data_frame.discount_df
onlinesales_df = data_frame.onlinesales_df

#데이터 전처리
#ID 형식들 숫자로 변환
#제품ID랑 카테고리 연결
#텍스트데이터 벡터로 변환 (제품카테고리, 고객지역)
#코사인유사도 계산