import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DB.db_mysql import select_apt_competition,select_unranked_competition_1,select_upcoming_applications
 


# 컬럼명을 영어 -> 한글로 매핑
COLUMN_MAPPING = {
    "region": "지역",
    "housing_type": "주택 유형",
    "sale_or_lease": "분양/임대",
    "apartment_name": "아파트명",
    "construction_company": "건설사",
    "contact": "연락처",
    "announcement_date": "공고일",
    "application_period_start": "청약 접수 시작일",
    "application_period_end": "청약 접수 종료일",
    "result_announcement": "당첨자 발표일",
    "subscription_type" : "주택 유형",
    "house_type" : "주택 유형",
    "supply_units" : "공급 세대수",
    "application_count" : "신청자 수",
    "competition_rate" : "경쟁률",
    "application_result" : "청약 결과",
    "rank" : "순위",
    "rank_region" : "순위 별 지역",
}
def web_apt_competition():
    df = select_apt_competition()

    # None 데이터를 '-'로 대체
    df = df.fillna('-')
    
    grouped = df.groupby('apartment_name')
    grouped_data = []
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    # 각 아파트 이름별로 출력
    for name, group in grouped:
        table_html = group.to_html(classes="table table-bordered", index=False)
        grouped_data.append({
            'apartment_name': name,
            'data': table_html
        })

    
    return grouped_data

def web_apt_competition_simple():
    df = select_apt_competition()

    # application_count 열을 문자열로 변환 후 숫자로 변환 (결측값 및 특수문자 처리)
    df['application_count'] = (
        df['application_count']
        .astype(str)  # 문자열로 변환
        .str.replace(r'[^\d]', '', regex=True)  # 숫자 이외의 문자 제거
        .replace('', '0')  # 빈 문자열을 0으로 대체
        .astype(float)  # 숫자(float)로 변환
    )

    # supply_units 열도 숫자로 변환
    df['supply_units'] = pd.to_numeric(df['supply_units'], errors='coerce').fillna(0)

    grouped = df.groupby('apartment_name')
    grouped_data = []

    # 각 아파트 이름별로 출력
    for name, group in grouped:
        # 전체 경쟁률 계산
        total_supply = group['supply_units'].sum()
        total_application = group['application_count'].sum()
        competition_rate = round(total_application / total_supply if total_supply > 0 else 0,2)

        # application_result 열 처리
        application_result = group['application_result'].unique()
        application_result = application_result[0]

        grouped_data.append({
            'apartment_name': name,
            'total_competition_rate': competition_rate,
            'application_result' : application_result
        })

    return grouped_data






def web_unranked_competition():
    df = select_unranked_competition_1()

    # None 데이터를 '-'로 대체
    df = df.fillna('-')
    
    grouped = df.groupby('apartment_name')
    grouped_data = []

    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # 각 아파트 이름별로 출력
    for name, group in grouped:
        table_html = group.to_html(classes="table table-bordered", index=False)
        grouped_data.append({
            'apartment_name': name,
            'data': table_html
        })

    return grouped_data


def web_apt_unranked_simple():
    df = select_unranked_competition_1()

    # application_count 열을 문자열로 변환 후 숫자로 변환 (결측값 및 특수문자 처리)
    df['application_count'] = (
        df['application_count']
        .astype(str)  # 문자열로 변환
        .str.replace(r'[^\d]', '', regex=True)  # 숫자 이외의 문자 제거
        .replace('', '0')  # 빈 문자열을 0으로 대체
        .astype(float)  # 숫자(float)로 변환
    )

    # supply_units 열도 숫자로 변환
    df['supply_units'] = pd.to_numeric(df['supply_units'], errors='coerce').fillna(0)

    grouped = df.groupby('apartment_name')
    
    grouped_data = []

    # 각 아파트 이름별로 출력
    for name, group in grouped:
        # 전체 경쟁률 계산
        total_supply = group['supply_units'].sum()
        total_application = group['application_count'].sum()
        competition_rate = round(total_application / total_supply if total_supply > 0 else 0,2)

        # application_result 열 처리
        application_result = group['application_result'].unique()
        application_result = application_result[0]

        grouped_data.append({
            'apartment_name': name,
            'total_competition_rate': competition_rate,
            'application_result' : application_result
        })

    return grouped_data











def web_upcoming_applications_simple(table):
    # table = "apt_housing_application_basic_info"
    # table = "unranked_housing_application_basic_info"
    df = select_upcoming_applications(table)

    # None 데이터를 '-'로 대체
    df = df.fillna('-')
    
    data = []

    for idx, row in df.iterrows():        
        data.append ({
            'apartment_name': row["apartment_name"],
            'application_period_start': row["application_period_start"],
            'region' : row["region"]
        })

    return data




def web_upcoming_applications(table):
    # 테이블 데이터를 조회 (예시 데이터프레임 생성)
    df = select_upcoming_applications(table)

    # None 데이터를 '-'로 대체
    df = df.fillna('-')

    # 컬럼명을 한글로 변경
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    data = []
    for idx, row in df.iterrows():
        # DataFrame 행을 HTML 테이블로 변환
        row_df = row.to_frame().T
        table_html = row_df.to_html(classes="table table-bordered", index=False, escape=False)
        data.append({
            'apartment_name': row["아파트명"],  # 한글 컬럼명으로 변경
            'data': table_html
        })
    return data
