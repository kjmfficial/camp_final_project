import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import sys
import matplotlib as mpl
import io
import base64

 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DB.db_mysql import select_all

# 한글 폰트 설정 (Windows 환경에서 'Malgun Gothic' 사용)
mpl.rcParams['font.family'] = 'Malgun Gothic'
mpl.rcParams['axes.unicode_minus'] = False  # U+2212 대신 ASCII '-' 사용


# mysql_db에서 바꿔야함.
table = "competition"
df = select_all(table)

print(df)



def parse_value(value):
    if isinstance(value, str):  # 문자열인지 확인
        if value.startswith("(△"):  # 특수값 처리
            try:
                # "(△49)" 형식에서 숫자만 추출 후 음수로 변환
                return -int(value[2:-1])
            except ValueError:
                return None
        try:  # 숫자 변환 시도
            return float(value)
        except ValueError:  # 변환 실패 시 None 반환
            return None
    return value  # 문자열이 아니면 그대로 반환

def general_competition_graph(region, year):
    """
    특정 지역과 년도에 대한 월별 일반 청약 경쟁률 데이터를 시각화 (로그 스케일 활용, 양수는 파랑, 음수는 빨강).
    """
    # 'parse_value' 함수를 기존 데이터에 적용하여 처리
    df["processed_general_supply_competition_rate"] = df["general_supply_competition_rate"].apply(parse_value)

    # 'year_month'를 datetime으로 변환
    df["year_month"] = pd.to_datetime(df["year_month"])

    # 선택한 년도와 지역에 해당하는 데이터 필터링
    filtered_data = df[(df["year_month"].dt.year == year) & (df["region"] == region)]

    # 월별 데이터만 추출 (x축: 월, y축: 경쟁률)
    filtered_data["month"] = filtered_data["year_month"].dt.month
    grouped = filtered_data.groupby("month").agg({
        "processed_general_supply_competition_rate": "mean"
    }).reset_index()

    # 막대 그래프 그리기
    plt.figure(figsize=(10, 6))
    colors = grouped["processed_general_supply_competition_rate"].apply(
        lambda x: "blue" if x > 0 else "red"
    )
    plt.bar(
        grouped["month"],
        grouped["processed_general_supply_competition_rate"],
        color=colors
    )

    # 로그 스케일 적용
    plt.yscale('symlog', linthresh=1)  # 작은 값은 선형, 큰 값은 로그

    plt.title(f"General Supply Competition Rate in {region} for {year}")
    plt.xlabel("Month")
    plt.ylabel("Competition Rate (Log Scale)")
    plt.xticks(ticks=range(1, 13), labels=[f"{m}월" for m in range(1, 13)])
    plt.axhline(0, color="black", linewidth=0.8, linestyle="--")  # 기준선 추가
    plt.tight_layout()

    # 그래프를 Base64로 변환
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return graph_base64


def special_competition_graph(region, year):
    """
    특정 지역과 년도에 대한 월별 특별 청약 경쟁률 데이터를 시각화 (로그 스케일 활용, 양수는 파랑, 음수는 빨강).
    """
    # 'parse_value' 함수를 기존 데이터에 적용하여 처리
    df["processed_special_supply_competition_rate"] = df["special_supply_competition_rate"].apply(parse_value)

    # 'year_month'를 datetime으로 변환
    df["year_month"] = pd.to_datetime(df["year_month"])

    # 선택한 년도와 지역에 해당하는 데이터 필터링
    filtered_data = df[(df["year_month"].dt.year == year) & (df["region"] == region)]

    # 월별 데이터만 추출 (x축: 월, y축: 경쟁률)
    filtered_data["month"] = filtered_data["year_month"].dt.month
    grouped = filtered_data.groupby("month").agg({
        "processed_special_supply_competition_rate": "mean"
    }).reset_index()

    # 막대 그래프 그리기
    plt.figure(figsize=(10, 6))
    colors = grouped["processed_special_supply_competition_rate"].apply(
        lambda x: "blue" if x > 0 else "red"
    )
    plt.bar(
        grouped["month"],
        grouped["processed_special_supply_competition_rate"],
        color=colors
    )

    # 로그 스케일 적용
    plt.yscale('symlog', linthresh=1)  # 작은 값은 선형, 큰 값은 로그

    plt.title(f"Special Supply Competition Rate in {region} for {year}")
    plt.xlabel("Month")
    plt.ylabel("Competition Rate (Log Scale)")
    plt.xticks(ticks=range(1, 13), labels=[f"{m}월" for m in range(1, 13)])
    plt.axhline(0, color="black", linewidth=0.8, linestyle="--")  # 기준선 추가
    plt.tight_layout()

    # 그래프를 Base64로 변환
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return graph_base64