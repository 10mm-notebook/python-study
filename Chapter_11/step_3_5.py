from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from step_1 import OUT_DIR
from step_2_1 import OUT_2_1
from step_2_3 import OUT_2_3
from step_3_2 import OUT_3_2

OUT_3_5 = OUT_DIR / f"step_3_5(2024.1~2025.8).png"


def transaction_frequency_to_img():
    """
    자치구별 거래 빈도를 계산하고 단계 구분도로 시각화하여 저장합니다.
    """
    # 1. 아파트 실거래가 데이터 읽기
    df_apt = pd.read_csv(OUT_2_3, dtype={"지역코드": str})

    # 2. 자치구별 거래 빈도 계산
    df_freq = df_apt.groupby("지역코드").size().reset_index(name="거래량")

    # 3. 주소 및 지리 데이터 읽기
    df_sido_sgg = pd.read_csv(OUT_2_1, dtype={"sido_sgg": str})
    gdf_geo = gpd.read_file(OUT_3_2, encoding="utf-8")

    # 4. 데이터 병합
    # 거래량 데이터와 주소 데이터 병합
    df_merged = pd.merge(df_sido_sgg, df_freq, left_on="sido_sgg", right_on="지역코드", how="inner")
    # 위 결과와 지리 데이터 병합
    gdf_final = pd.merge(gdf_geo, df_merged, left_on="adm_nm", right_on="locatadd_nm", how="inner")

    # 5. 시각화
    sns.set_theme(context="poster", font="Malgun Gothic")
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    gdf_final.plot(
        column="거래량",
        cmap="Reds",  # 거래량이 많을수록 진한 빨간색으로 표시
        edgecolor="k",
        legend=True,
        legend_kwds={"label": "아파트 거래량 (건)", "orientation": "vertical"},
        ax=ax,
    )
    ax.set_axis_off()
    ax.set_title("서울시 자치구별 아파트 거래량 (2024.1~2025.8)")
    fig.set_layout_engine("tight")
    fig.savefig(OUT_3_5)


if __name__ == "__main__":
    transaction_frequency_to_img()
    print(f"거래 빈도 시각화가 완료되어 '{OUT_3_5}' 파일로 저장되었습니다.")
