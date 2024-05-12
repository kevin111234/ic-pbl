import pandas
import pymysql
from sqlalchemy import create_engine
import data_save

# 데이터 불러오기 함수
def db_pull_out(select,dataframe,sql_pswd):
    engine = data_save.sql_setting_Alchemy(sql_pswd)
    query = f"SELECT {select} FROM {dataframe}"
    return engine,query

# 칼럼명으로 두 데이터 결합해서 불러오기 함수 (조건 1개 버전)
def db_group_1column(select,dataframe1,dataframe2,group_column,sql_pswd, morequery=None):
    engine = data_save.sql_setting_Alchemy(sql_pswd)
    if morequery is None:
        query = f'''SELECT {select} 
        FROM {dataframe1} JOIN {dataframe2} ON {dataframe1}.{group_column}={dataframe2}.{group_column}
        '''
    else:
        query = f'''SELECT {select} 
        FROM {dataframe1} JOIN {dataframe2} ON {dataframe1}.{group_column}={dataframe2}.{group_column}
        {morequery}
        '''
    return engine,query

# 칼럼명으로 두 데이터 결합해서 불러오기 함수 (조건 2개 버전)
def db_group_2column(select, dataframe1,dataframe2,group_column1,group_column2,sql_pswd, morequery=None):
    engine = data_save.sql_setting_Alchemy(sql_pswd)
    if morequery is None:
        query = f'''SELECT {select}
        FROM {dataframe1} JOIN {dataframe2} 
        ON {dataframe1}.{group_column1}={dataframe2}.{group_column1}
        AND {dataframe1}.{group_column2}={dataframe2}.{group_column2}
        '''
    else:
        query = f'''SELECT {select}
        FROM {dataframe1} JOIN {dataframe2} 
        ON {dataframe1}.{group_column1}={dataframe2}.{group_column1}
        AND {dataframe1}.{group_column2}={dataframe2}.{group_column2}
        {morequery}
        '''
    return engine,query