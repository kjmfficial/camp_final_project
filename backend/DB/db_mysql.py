# mysql
import pymysql
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from typing import List, Dict
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import csv

 
load_dotenv()

# mysql 연결 URI
user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
host = os.environ.get('MYSQL_HOST') # 탄력적ip사용해야할듯 ..
db = os.environ.get('MYSQL_DB')
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_query(query: str, params: dict):
    """
    데이터베이스 쿼리를 실행하고 결과를 반환합니다.
    """
    session = SessionLocal()
    try:
        result = session.execute(text(query), params)
        # 각 Row 객체를 딕셔너리로 변환
        return [dict(row._mapping) for row in result.fetchall()]  # ._mapping을 사용하여 딕셔너리 변환
    finally:
        session.close()

def mysql_insert(query,values):    
    with engine.connect() as conn:
        try:
            conn.execute(query, values)
            conn.commit() 
            print(" 데이터 삽입성공!")
        except Exception as e:
            print(f" DB에 넣는거 실패함 ㅜㅜ 고쳐라: {e}")


def apt_housing_application_basic_info_insert(data):
    try:
        # CSV 데이터 읽기
        df = data

        df = df[df.iloc[:, 0] != "총합계"]

        # '청약결과' 컬럼의 공백 처리
        df = df.replace({np.nan: None, '-': None})

        df['application_period_start'] = df['청약기간'].apply(lambda x: x.split(' ~ ')[0].strip())
        df['application_period_end'] = df['청약기간'].apply(lambda x: x.split(' ~ ')[1].strip())
        df = df.replace({np.nan: None})
        df = df.drop(df.columns[-4], axis=1)

        # 컬럼명 변경
        df.columns = [
            "region", "housing_type", "sale_or_lease", "apartment_name", 
            "construction_company", "contact", "announcement_date", "result_announcement", "application_period_start", 
            "application_period_end"
        ]

        # 삽입할 쿼리
        query = text("""
            INSERT INTO apt_housing_application_basic_info (
                region, housing_type, sale_or_lease, apartment_name, construction_company,
                contact, announcement_date, application_period_start, application_period_end, result_announcement
            ) VALUES (
                :region, :housing_type, :sale_or_lease, :apartment_name, :construction_company,
                :contact, :announcement_date, :application_period_start, :application_period_end, :result_announcement
            )
        """)


        # 데이터프레임을 순회하며 각 행을 삽입
        for _, row in df.iterrows():
            values = {
                "region": row["region"],
                "housing_type": row["housing_type"],
                "sale_or_lease": row["sale_or_lease"],
                "apartment_name": row["apartment_name"],
                "construction_company": row["construction_company"],
                "contact": row["contact"],
                "announcement_date": row["announcement_date"],
                "application_period_start": row["application_period_start"],
                "application_period_end": row["application_period_end"],
                "result_announcement": row["result_announcement"],
            }
            mysql_insert(query, values)
        print("모든 기본정보 데이터 삽입 완료!")

    except Exception as e:
        print(f"CSV 삽입 중 오류 발생: {e}")


def apt_housing_application_basic_info_select():
    session = SessionLocal()
    try:
        query = text("SELECT apartment_name FROM apt_housing_application_basic_info" )
        result = session.execute(query)
        items = [{"apartment_name": row[0]} for row in result]
    finally:
        session.close()
    return items



def apt_housing_competition_rate_insert(data):
    try:
        df = data

        df = df[df.iloc[:, 0] != "총합계"]

                # 컬럼명 변경
        df.columns = [
            "house_type", "supply_units", "rank", "rank_region", "application_count", 
            "competition_rate", "application_result", "region", "score_min", "score_max", "score_avg","apartment_name"
        ]
        
        # 결측값 및 '-' 값 처리
        df = df.replace({np.nan: None, '-': None})
        
        print("굳")

        insert_query = text("""
            INSERT INTO apt_housing_competition_rate (
                house_type, supply_units, `rank`, rank_region, application_count, 
                competition_rate, application_result, region, score_min, score_max, score_avg,apartment_name
            ) VALUES (
                :house_type, :supply_units, :rank, :rank_region, :application_count, 
                :competition_rate, :application_result, :region, :score_min, :score_max, :score_avg, :apartment_name
            )
        """)

        # 데이터 삽입
        for _, row in df.iterrows():
            values = {
                "apartment_name" : row["apartment_name"],
                "house_type": row["house_type"],
                "supply_units": row["supply_units"],
                "rank": row["rank"],
                "rank_region": row["rank_region"],
                "application_count": row["application_count"],
                "competition_rate": row["competition_rate"],
                "application_result": row["application_result"],
                "region": row["region"],
                "score_min": row["score_min"],
                "score_max": row["score_max"],
                "score_avg": row["score_avg"]
            }
            mysql_insert(insert_query, values)
        print("경쟁률 데이터 삽입 완료!")

    except Exception as e:
        print(f"CSV 삽입 중 오류 발생: {e}")

def apt_housing_competition_rate_select():
    session = SessionLocal()
    try:
        query = text("SELECT apartment_name FROM apt_housing_competition_rate" )
        result = session.execute(query)
        items = [{"apartment_name": row[0]} for row in result]
    finally:
        session.close()
    return items
 

def apt_housing_application_status_insert(data):
    try:
        df = data

        df = df[df.iloc[:, 0] != "총합계"]
        df = df.replace({np.nan: None, '-': None})
        
        df.columns = [
            "house_type", "supply_units", "region", "multi_child_family", "newlyweds", 
            "first_time_homebuyer", "youth", "elderly_support", "newborn_general", "institution_recommended", "transfer_institution","application_status","apartment_name"
        ]

        print("굳!")

        # 삽입할 쿼리
        insert_query = text("""
            INSERT INTO apt_housing_application_status (
                house_type, supply_units, region, multi_child_family, 
                newlyweds, first_time_homebuyer, youth, elderly_support, 
                newborn_general, institution_recommended, transfer_institution, application_status, apartment_name
            ) VALUES (
                :house_type, :supply_units, :region, :multi_child_family, 
                :newlyweds, :first_time_homebuyer, :youth, :elderly_support, 
                :newborn_general, :institution_recommended, :transfer_institution, :application_status, :apartment_name
            )
        """)

        # 데이터프레임을 순회하며 각 행을 삽입
        for _, row in df.iterrows():
            values = {
                "house_type": row["house_type"],
                "supply_units": row["supply_units"],
                "region": row["region"],

                "multi_child_family": row["multi_child_family"],
                "newlyweds": row["newlyweds"],
                "first_time_homebuyer": row["first_time_homebuyer"],
                "youth": row["youth"],
                "elderly_support": row["elderly_support"],
                "newborn_general": row["newborn_general"],
                "institution_recommended": row["institution_recommended"],
                "transfer_institution": row["transfer_institution"],
                "application_status": row["application_status"],
                "apartment_name": row["apartment_name"]
            }
            mysql_insert(insert_query, values)

        print("모집현황 데이터 삽입 완료!")

    except Exception as e:
        print(f"CSV 삽입 중 오류 발생: {e}")

def apt_housing_application_status_select():
    session = SessionLocal()
    try:
        query = text("SELECT DISTINCT apartment_name FROM apt_housing_application_status;" )
        result = session.execute(query)
        items = [{"apartment_name": row[0]} for row in result]
    finally:
        session.close()
    return items



def unranked_housing_application_basic_info_insert(data):
    try:

        df = data

        df['application_period_start'] = df['청약기간'].apply(lambda x: x.split(' ~ ')[0].strip())
        df['application_period_end'] = df['청약기간'].apply(lambda x: x.split(' ~ ')[1].strip())
        df = df.replace({np.nan: None})
        df = df.drop(columns=['청약기간'])

        df.columns = [
            "region", "apartment_name", "construction_company", "announcement_date", "result_announcement", 
            "application_period_start", "application_period_end"
        ]
        df['subscription_type'] = '무순위'

        print(df.columns)
        # 삽입할 쿼리
        query = text("""
            INSERT INTO unranked_housing_application_basic_info (
                region, apartment_name, construction_company,
                announcement_date, application_period_start, application_period_end, result_announcement, subscription_type
            ) VALUES (
                :region, :apartment_name, :construction_company,
                :announcement_date, :application_period_start, :application_period_end, :result_announcement, :subscription_type
            )
        """)


        # 데이터프레임을 순회하며 각 행을 삽입
        for _, row in df.iterrows():
            values = {
                "region": row["region"],
                "apartment_name": row["apartment_name"],
                "construction_company": row["construction_company"],
                "announcement_date": row["announcement_date"],
                "application_period_start": row["application_period_start"],
                "application_period_end": row["application_period_end"],
                "result_announcement": row["result_announcement"],
                "subscription_type": row["subscription_type"],
            }
            mysql_insert(query, values)
        print("모든 데이터 삽입 완료!")

    except Exception as e:
        print(f"CSV 삽입 중 오류 발생: {e}")

def unranked_housing_application_basic_info_select():
    session = SessionLocal()
    try:
        query = text("SELECT apartment_name FROM unranked_housing_application_basic_info" )
        result = session.execute(query)
        items = [{"apartment_name": row[0]} for row in result]
    finally:
        session.close()
    return items

def unranked_housing_competition_rate_insert(data):
    try:
        df = data

        print(type(len(df.columns)))
        if len(df.columns) == 6:
            # 컬럼명 변경
            
            df.columns = [
                "house_type", "supply_units", "application_count", 
                "competition_rate", "application_result", "apartment_name"
            ]
            
            # 결측값 및 '-' 값 처리
            df = df.replace({np.nan: None, '-': None})

            
            insert_query = text("""
                INSERT INTO unranked_housing_competition_rate_1 (
                    house_type, supply_units, application_count, 
                    competition_rate, application_result, apartment_name
                ) VALUES (
                    :house_type, :supply_units, :application_count, 
                    :competition_rate, :application_result, :apartment_name
                )
            """)

            # 데이터 삽입
            for _, row in df.iterrows():
                values = {
                    "apartment_name" : row["apartment_name"],
                    "house_type": row["house_type"],
                    "supply_units": row["supply_units"],
                    "application_count": row["application_count"],
                    "competition_rate": row["competition_rate"],
                    "application_result": row["application_result"]
                }
                mysql_insert(insert_query, values)
        else:
            print(df.columns)
            # 컬럼명 변경
            df.columns = [
                "house_type", "supply_units", "classification", "multi_child_family", "newlyweds", 
                "first_time_homebuyer", "elderly_support", "institution_recommended", "general_supply", "application_result", "apartment_name"
            ]
            # 결측값 및 '-' 값 처리
            df = df.replace({np.nan: None, '-': None})
            
            
            insert_query = text("""
                INSERT INTO unranked_housing_competition_rate_2 (
                    house_type, supply_units, classification, multi_child_family, newlyweds, 
                    first_time_homebuyer, elderly_support, institution_recommended, general_supply, application_result, apartment_name
                ) VALUES (
                    :house_type, :supply_units, :classification, :multi_child_family, :newlyweds, 
                    :first_time_homebuyer, :elderly_support, :institution_recommended, :general_supply, :application_result, :apartment_name
                )
            """)

            # 데이터 삽입
            for _, row in df.iterrows():
                values = {
                    "apartment_name" : row["apartment_name"],
                    "house_type": row["house_type"],
                    "supply_units": row["supply_units"],
                    "classification": row["classification"],
                    "multi_child_family": row["multi_child_family"],
                    "newlyweds": row["newlyweds"],
                    "first_time_homebuyer": row["first_time_homebuyer"],
                    "elderly_support": row["elderly_support"],
                    "institution_recommended": row["institution_recommended"],
                    "general_supply": row["general_supply"],
                    "application_result": row["application_result"]
                }
                mysql_insert(insert_query, values)
        print("모든 데이터 삽입 완료!")

    except Exception as e:
        print(f"CSV 삽입 중 오류 발생: {e}")

def unranked_housing_competition_rate_select():
    session = SessionLocal()
    try:
        query = text("SELECT apartment_name FROM unranked_housing_competition_rate_1 UNION SELECT apartment_name FROM unranked_housing_competition_rate_2" )
        result = session.execute(query)
        items = [{"apartment_name": row[0]} for row in result]
    finally:
        session.close()
    return items

def apt_schedule_insert(apartment_name,subscription_type,application_period_start,application_period_end):
    query = text("INSERT INTO apt_schedule VALUES (:val1, :val2, :val3, :val4)") # colunm = item_id, height, weight, size, gender
    values = {"val1": apartment_name, "val2": subscription_type, "val3": application_period_start, "val4": application_period_end}

    with engine.connect() as conn:
        try:
            conn.execute(query, values)  
            conn.commit()
            print("tb_insert_crawling_review : 데이터 삽입 성공~~~~!!!!")
        except Exception as e:
            print(f"tb_insert_crawling_review : DB에 넣는거 실패함 ㅜㅜ 빨리 고쳐라: {e}")

def apt_schedule_select():
    session = SessionLocal()
    try:
        query = text("SELECT apartment_name FROM apt_schedule" )
        result = session.execute(query)
        items = [{"apartment_name": row[0]} for row in result]
    finally:
        session.close()
    return items

def some_condition(table_name, home_name):
    # 예시: 특정 테이블에 해당 아파트 이름이 존재하는지 확인
    query = text(f"SELECT COUNT(*) FROM {table_name} WHERE apartment_name = :apartment_name")
    with engine.connect() as conn:
        result = conn.execute(query, {"apartment_name": home_name}).scalar()
        return result > 0  

def delete(table, apartment_name):
    # SQL 문에서 문자열 바인딩을 위해 파라미터 사용
    query = text(f"DELETE FROM {table} WHERE apartment_name = :apartment_name")
    
    with engine.connect() as conn:
        try:
            # 쿼리 실행 시 파라미터 전달
            conn.execute(query, {"apartment_name": apartment_name})
            conn.commit()
            print(f"{table} 테이블의 {apartment_name} 데이터 삭제 완료!")
            
        except Exception as e:
            print(f"delete : DB에서 삭제 실패함 ㅜㅜ 근데 이게 실패할 수가 있는건가??: {e}")


def login():
    SQL = "SELECT id,password,bankbook,email,resident_number,phone_number,address,name FROM login" 

    with engine.connect() as conn:
        df = pd.read_sql(SQL, conn)
    return df

def login_save(id, passwd,bankbook,email,resident_number,phone_number,address,name):
    query = text("INSERT INTO login VALUES (:val1, :val2, :val3, :val4, :val5, :val6, :val7, :val8)")  # colunm = item_id, review
    values = {"val1": id, "val2": passwd, "val3": bankbook, "val4": email, "val5": resident_number, "val6": phone_number, "val7": address, "val8": name}

    with engine.connect() as conn:
        try:
            conn.execute(query, values)  
            conn.commit()
            print("login : 데이터 삽입 성공~~~~!!!!")
        except Exception as e:
            print(f"login : DB에 넣는거 실패함 ㅜㅜ 고쳐줘잉: {e}")

def check_duplicate_id(user_id: str) -> bool:
    # SQL 쿼리를 사용해 ID 중복 확인
    with engine.connect() as connection:
        sql = text("SELECT COUNT(*) FROM login WHERE id = :id")
        result = connection.execute(sql, {"id": user_id}).scalar()
        return result > 0  # 중복된 ID가 존재하면 True 반환



def get_schedule_details(apartment_name: str) -> Dict:
    session = SessionLocal()
    try:

        query = text("""
        SELECT 
            apartment_name, 
            application_period_start, 
            application_period_end, 
            region, 
            housing_type, 
            sale_or_lease, 
            construction_company, 
            contact, 
            result_announcement
        FROM apt_housing_application_basic_info
        WHERE apartment_name = :apartment_name

        UNION

        SELECT 
            apartment_name, 
            application_period_start, 
            application_period_end, 
            region, 
            NULL AS housing_type, 
            NULL AS sale_or_lease, 
            construction_company, 
            NULL AS contact, 
            result_announcement
        FROM unranked_housing_application_basic_info
        WHERE apartment_name = :apartment_name
        """)

        result = session.execute(query, {"apartment_name": apartment_name}).fetchone()

        if result:
            return {
                "apartment_name": result[0],
                "application_period_start": result[1].isoformat() if result[1] else None,
                "application_period_end": result[2].isoformat() if result[2] else None,
                "region": result[3],
                "housing_type": result[4],
                "sale_or_lease" : result[5],
                "construction_company" : result[6],
                "contact" : result[7],
                "result_announcement" : result[8]

            }
        return {}
    finally:
        session.close()

def get_filtered_schedule(
    start: str,
    end: str,
    special: bool,
    priority1: bool,
    priority2: bool,
    unranked: bool,
) -> List[Dict]:
    if  not (special or priority1 or priority2 or unranked):
        # 모든 필터가 비활성화된 경우 빈 리스트 반환
        return []
    filter_conditions = {
        "special": "특별공급",
        "priority1": "1순위",
        "priority2": "2순위",
        "unranked": "무순위",
    }
    active_filters = [key for key, value in filter_conditions.items() if locals()[key]]
    filter_query = " OR ".join(f"subscription_type = :{key}" for key in active_filters)

    if filter_query:
        filters1 = f" AND ({filter_query})"
        filters2 = f" AND ({filter_query})"
    else:
        filters1 = filters2 = ""

    query = f"""
        SELECT 
            apartment_name, 
            application_period_start, 
            subscription_type
        FROM apt_schedule
        WHERE application_period_start >= :start 
            AND application_period_start <= :end
            {filters1}

        UNION

        SELECT
            apartment_name,
            application_period_start,
            subscription_type
        FROM unranked_housing_application_basic_info
        WHERE application_period_start >= :start 
            AND application_period_start <= :end
            {filters2}
    """

    params = {
        "start": start,
        "end": end,
        **{key: filter_conditions[key] for key in active_filters},
    }

    results = execute_query(query, params)

    color_map = {
        "특별공급": "#F38EB8",
        "1순위": "#4361ee",
        "2순위": "#57b6fe",
        "무순위": "gray",
    }

    return [
        {
            "start": row["application_period_start"].isoformat(),
            "title": row["apartment_name"],
            "color": color_map.get(row["subscription_type"], "black"),
            "extendedProps": {"subscription_type": row["subscription_type"]},
        }
        for row in results
    ]


def select_all(table):
    query = f"select * from {table}"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def select_competiton_all(table,region,year,select):
    query = f"SELECT month(`year_month`), {select} FROM {table} WHERE year(`year_month`) = {year} and region = '{region}'"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def select_apt_competition():
    query = """
    WITH ranked_apartments AS (
        SELECT apartment_name, MAX(announcement_date) AS latest_announcement_date
        FROM lgu.apt_housing_application_basic_info
        GROUP BY apartment_name
        ORDER BY COUNT(*) DESC
        LIMIT 15
    )
    SELECT b.apartment_name	, a.application_period_start ,b.house_type ,b.supply_units ,b.rank ,b.rank_region ,b.application_count ,b.competition_rate ,b.application_result 
    FROM lgu.apt_housing_application_basic_info a
    LEFT JOIN lgu.apt_housing_competition_rate b
        ON a.apartment_name = b.apartment_name
    WHERE a.apartment_name IN (SELECT apartment_name FROM ranked_apartments)
    AND a.announcement_date = (
        SELECT latest_announcement_date
        FROM ranked_apartments
        WHERE apartment_name = a.apartment_name
    )
    AND (b.application_result IS NULL OR b.application_result != '청약 접수일 미도래')
    order by a.application_period_start desc;"""
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df



def select_unranked_competition_1():
    query = """
        SELECT 
            uha.application_period_start, rate1.*
        FROM lgu.unranked_housing_application_basic_info uha
        LEFT JOIN lgu.unranked_housing_competition_rate_1 rate1
            ON uha.apartment_name = rate1.apartment_name
        WHERE rate1.application_result != '청약접수일 미도래';
            """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def select_unranked_competition_2():
    query = """
        SELECT 
            uha.application_period_start, rate2.*
        FROM lgu.unranked_housing_application_basic_info uha
        LEFT JOIN lgu.unranked_housing_competition_rate_2 rate2
            ON uha.apartment_name = rate2.apartment_name
        WHERE rate2.application_result != '청약접수일 미도래';
            """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df



# 청약 경쟁률 정보 삽입, 청약 분양가 정보 삽입
def csv_save(csv_file_path, table_name):
    df = pd.read_csv(csv_file_path, encoding="cp949")
    df.to_sql(name=table_name, con=engine, if_exists="replace", index=False,)
    print(f"CSV 파일이 MySQL 테이블 '{table_name}'에 성공적으로 저장되었습니다.")


def select_upcoming_applications(table):
    query = f"""
        SELECT *
        FROM {table}
        WHERE application_period_start >= NOW();
            """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def select_id(name, email):
    session = SessionLocal()
    try:
        query = text("""
            SELECT id
            FROM login
            WHERE name = :name AND email = :email
        """)
        result = session.execute(query, {"name": name, "email": email})
        return result.fetchall()
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        session.close()

        
def update_password(name, id ,email,password):
    session = SessionLocal()
    try:
        query = text("""
            UPDATE login
                SET password = :password
                WHERE name = :name AND email = :email AND id = :id
        """)
        result = session.execute(query, {"name": name, "email": email, "id": id,"password": password})
        return result.fetchall()
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        session.close()

def rag_data(table):
    SQL = f"SELECT * FROM {table}" 

    with engine.connect() as conn:
        df = pd.read_sql(SQL, conn)
    return df


def select_json(table):
    session = SessionLocal()
    try:
        query = text(f"select * from {table}")  # text로 쿼리 작성
        result = session.execute(query)
        rows = result.mappings().all()  # Row 객체를 dict 형태로 변환
        return [dict(row) for row in rows]  # 각 행을 dict로 변환하여 리스트로 반환
    finally:
        session.close()


if __name__ == "__main__":
    # csv_file_path = "./data/한국부동산원_지역별 청약 경쟁률 정보_20241130.csv"
    # tabel_name = "competition"
    # csv_save(csv_file_path, tabel_name)

    # csv_file_path = "./data/한국부동산원_지역별 청약 평균 분양가 정보_20241130.csv"
    # tabel_name = "housing_price"
    # csv_save(csv_file_path, tabel_name)
    
    # print(select_competiton_all("competition","서울",2024,"general_supply_competition_rate"))

    # print(select_id("강이삭","wbsldj59@naver.com")[0][0])
    
    # print(rag_data("apt_housing_application_basic_info"))
    pass