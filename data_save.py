import pymysql
import sqlalchemy

# sql 테이블 생성, 데이터 저장 쿼리
customer_table = f"""
    CREATE TABLE IF NOT EXISTS customer_info (
        고객ID CHAR(9) PRIMARY KEY,
        성별 CHAR(1),
        고객지역 VARCHAR(255),
        가입기간 INT
        );
    """
customer_save = f"""
    insert into customer_info (고객ID,성별,고객지역,가입기간)
    values (%s,%s,%s,%s,%s)
    on duplicate key update
    고객ID = VALUES(고객ID),
    성별 = VALUES(성별),
    고객지역 = VALUES(고객지역),
    가입기간 = VALUES(가입기간);
"""

discount_table = f"""
    CREATE TABLE IF NOT EXISTS discount_info (
        월 INT,
        제품카테고리 VARCHAR(255),
        쿠폰코드 VARCHAR(50) PRIMARY KEY,
        할인율 DECIMAL(3,1)
        );
    """
discount_save = f"""
    insert into discount_info (월, 제품카테고리, 쿠폰코드, 할인율)
    values (%s,%s,%s,%s)
    on duplicate key update
    월 = VALUES(월),
    제품카테고리 = VALUES(제품카테고리),
    쿠폰코드 = VALUES(쿠폰코드),
    할인율 = VALUES(할인율),;
"""

marketing_table = f"""
    CREATE TABLE IF NOT EXISTS marketing_info (
        날짜 DATE PRIMARY KEY,
        오프라인비용 INT,
        온라인비용 INT,
        월 INT
        );
    """
marketing_save = f"""
    insert into marketing_info (날짜, 오프라인비용, 온라인비용, 월)
    values (%s,%s,%s,%s)
    on duplicate key update
    날짜 = VALUES(날짜),
    오프라인비용 = VALUES(오프라인비용),
    온라인비용 = VALUES(온라인비용),
    월 = VALUES(월);
"""

onlinesales_table = f"""
    CREATE TABLE IF NOT EXISTS onlinesales_info (
        고객ID CHAR(9),
        거래ID CHAR(16) PRIMARY KEY,
        날짜 DATE,
        제품ID CHAR(12),
        제품카테고리 VARCHAR(255),
        수량 INT,
        평균금액 INT,
        배송비 INT,
        쿠폰상태 VARCHAR(10),
        월 INT
        );
    """
onlinesales_save = f"""
    insert into onlinesales_info (고객ID, 거래ID, 날짜, 제품ID, 제품카테고리, 수량, 평균금액, 배송료, 쿠폰상태, 월)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    on duplicate key update
    고객ID = VALUES(고객ID),
    거래ID = VALUES(거래ID),
    날짜 = VALUES(날짜),
    제품ID = VALUES(제품ID),
    제품카테고리 = VALUES(제품카테고리),
    수량 = VALUES(수량),
    평균금액 = VALUES(평균금액),
    배송료 = VALUES(배송료),
    쿠폰상태 = VALUES(쿠폰상태),
    월 = VALUES(월);
"""

table_list = [customer_table, discount_table, marketing_table, onlinesales_table]
save_list = [customer_save, discount_save, marketing_save, onlinesales_save]

# sql 연결 및 저장 함수
def sql_connect(dataframe):
    # DB 연결정보 할당
    db_host = "localhost"
    db_user = "root"
    db_password = input("sql 비밀번호를 입력하세요: ")
    db_name = "ic-pbl_analyze"
    db_port = 3306

    # DB 연결객체 생성
    con = pymysql.connect(user=db_user, 
                            passwd=db_password, 
                            host=db_host, 
                            db=db_name, 
                            charset='utf8')
    mycursor = con.cursor()
    try:
        # 커서 생성
        cursor = con.cursor()
        # sql 테이블이 없으면 테이블 생성
        for i in table_list:
            cursor.execute(i)
        # sql 저장 쿼리
        for j in save_list:
            args = dataframe.values.tolist()
            mycursor.executemany(j, args)
        # 커밋 후 연결 종료
        con.commit()
        con.close()
    except:
        #데이터베이스 연결에서 오류가 발생했을 때
        print("데이터베이스에 연결할 수 없습니다.")

# 데이터 저장 여부 결정 함수
def sql_save():
    while True:
        save = input("데이터를 DB에 저장하시겠습니까?(y/n): ")
        if save=="y":
            print("데이터를 DB에 저장합니다")
            sql_connect()
            break
        elif save=="n":
            print("데이터를 저장하지 않습니다")
            break
        else:
            print("잘못된 입력입니다. 다시 입력해주세요.")
