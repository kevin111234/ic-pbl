import pymysql
from sqlalchemy import create_engine

# sql 테이블 생성, 데이터 저장 쿼리
customer_table = """
    CREATE TABLE IF NOT EXISTS customer_info (
        고객ID CHAR(9) PRIMARY KEY,
        성별 CHAR(1),
        고객지역 VARCHAR(255),
        가입기간 INT,
        고객분류 VARCHAR(255)
        );
    """
customer_save = """
    insert into customer_info (고객ID,성별,고객지역,가입기간,고객분류)
    values (%s,%s,%s,%s,%s)
    on duplicate key update
    성별 = VALUES(성별),
    고객지역 = VALUES(고객지역),
    가입기간 = VALUES(가입기간),
    고객분류 = VALUES(고객분류);
"""

discount_table = """
    CREATE TABLE IF NOT EXISTS discount_info (
        월 INT,
        제품카테고리 VARCHAR(255),
        쿠폰코드 VARCHAR(50),
        할인율 INT
        );
    """
discount_save = """
    insert into discount_info (월, 제품카테고리, 쿠폰코드, 할인율)
    values (%s,%s,%s,%s)
    on duplicate key update
    월 = VALUES(월),
    제품카테고리 = VALUES(제품카테고리),
    쿠폰코드 = VALUES(쿠폰코드),
    할인율 = VALUES(할인율);
"""

marketing_table = """
    CREATE TABLE IF NOT EXISTS marketing_info (
        날짜 DATE PRIMARY KEY,
        오프라인비용 INT,
        온라인비용 INT,
        월 INT
        );
    """
marketing_save = """
    insert into marketing_info (날짜, 오프라인비용, 온라인비용, 월)
    values (%s,%s,%s,%s)
    on duplicate key update
    오프라인비용 = VALUES(오프라인비용),
    온라인비용 = VALUES(온라인비용),
    월 = VALUES(월);
"""

onlinesales_table = """
    CREATE TABLE IF NOT EXISTS onlinesales_info (
        고객ID CHAR(9),
        거래ID VARCHAR(50) PRIMARY KEY,
        날짜 DATE,
        제품ID CHAR(12),
        제품카테고리 VARCHAR(255),
        수량 INT,
        평균금액 FLOAT,
        배송료 FLOAT,
        쿠폰상태 VARCHAR(20),
        월 INT
        );
    """
onlinesales_save = """
    insert into onlinesales_info (고객ID, 거래ID, 날짜, 제품ID, 제품카테고리, 수량, 평균금액, 배송료, 쿠폰상태, 월)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    on duplicate key update
    고객ID = VALUES(고객ID),
    날짜 = VALUES(날짜),
    제품ID = VALUES(제품ID),
    제품카테고리 = VALUES(제품카테고리),
    수량 = VALUES(수량),
    평균금액 = VALUES(평균금액),
    배송료 = VALUES(배송료),
    쿠폰상태 = VALUES(쿠폰상태),
    월 = VALUES(월);
"""

# sql 연결 및 저장 함수
# DB 연결정보 할당
def sql_setting(sql_pswd):
    db_host = "localhost"
    db_user = "root"
    db_password = sql_pswd
    db_name = "ic-pbl_analyze"
    db_port = 3306

    # DB 연결객체 생성
    conn = pymysql.connect(user=db_user, 
                            passwd=db_password, 
                            host=db_host, 
                            db=db_name, 
                            charset='utf8mb4')
    # 커서 생성
    cursor = conn.cursor()
    return conn,cursor

def sql_setting_Alchemy(sql_pswd):
    db_host = "localhost"
    db_user = "root"
    db_password = sql_pswd
    db_name = "ic-pbl_analyze"
    db_port = 3306

    engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')
    return engine

# 테이블 생성
def create_tables(df_name, sql_pswd):
    conn, cursor = sql_setting(sql_pswd)
    table_list = [customer_table, discount_table, marketing_table, onlinesales_table]
    table_name = [s for s in table_list if df_name in s] 
    table_name = table_name[0]
    cursor.execute(table_name)

# 데이터프레임 삽입
def insert_data(dataframe,df_name,sql_pswd):
        conn, cursor = sql_setting(sql_pswd)
        # sql 저장 쿼리
        save_list = [customer_save, discount_save, marketing_save, onlinesales_save]
        args = dataframe.values.tolist()
        df_save = [s for s in save_list if df_name in s]
        df_save = df_save[0]
        cursor.executemany(df_save, args)
        conn.commit()
        # 커밋 후 연결 종료
        cursor.close()
        conn.close()

        #데이터베이스 연결에서 오류가 발생했을 때
        #print("데이터베이스에 연결할 수 없습니다.")

# 데이터 저장 여부 결정 함수
def save_to_db(dataframe, df_name,sql_pswd):
    while True:
        save = input("데이터를 DB에 저장하시겠습니까?(y/n): ")
        if save=="y":
            print("데이터를 DB에 저장합니다")
            conn, cursor = sql_setting(sql_pswd)
            create_tables(df_name,sql_pswd)
            insert_data(dataframe, df_name, sql_pswd)
            conn.commit()
            break
        elif save=="n":
            print("데이터를 저장하지 않습니다")
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")

