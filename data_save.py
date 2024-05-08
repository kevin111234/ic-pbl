import pymysql
from sqlalchemy import create_engine

# sql 테이블 생성 쿼리
customer_table = """
    CREATE TABLE IF NOT EXISTS customer_info (
        customer_id CHAR(9) PRIMARY KEY,
        gender CHAR(1),
        region VARCHAR(255),
        subscription_duration INT
        );
    """
discount_table = """
    CREATE TABLE IF NOT EXISTS discount_info (
        month INT,
        product_category VARCHAR(255),
        coupon_code VARCHAR(50) PRIMARY KEY,
        discount_rate DECIMAL(3,1)
        );
    """
marketing_table = """
    CREATE TABLE IF NOT EXISTS marketing_info (
        date DATE PRIMARY KEY,
        offline_cost INT,
        online_cost INT,
        month INT
        );
    """
onlinesales_table = """
    CREATE TABLE IF NOT EXISTS onlinesales_info (
        customer_id CHAR(9),
        trade_id CHAR(16) PRIMARY KEY,
        date DATE,
        product_id CHAR(12),
        product_category VARCHAR(255),
        amount INT,
        average_price INT,
        dilivery_cost INT,
        coupon_status VARCHAR(10),
        month INT
        );
    """

# sql 연결 및 저장 함수
def sql_save():
    # DB 연결정보 할당
    db_host = "localhost"
    db_user = "root"
    db_password = input("sql 비밀번호를 입력하세요: ")
    db_name = input("sql 데이터베이스 이름을 입력하세요: ")
    # DB 연결객체 생성
    conn = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    try:
        # 커서 생성
        cursor = conn.cursor()
        # sql 저장 쿼리
        # 커밋 후 연결 종료
        conn.commit()
        conn.close()
    except:
        #데이터베이스 연결에서 오류가 발생했을 때
        print("데이터베이스에 연결할 수 없습니다.")
