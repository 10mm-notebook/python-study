from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from step_1 import OUT_DIR
from step_2_1 import OUT_2_1
from step_2_3 import OUT_2_3
from step_3_2 import OUT_3_2

OUT_3_6 = OUT_DIR / f"step_3_6(2024.1~2025.8).png"


def price_change_to_img():
    """
    단위 면적당 평균 매매가 변동률을 계산하고
    단계 구분도로 시각화하여 저장합니다.
    """
    # 1. 데이터 읽기 및 전처리
    df_apt = pd.read_csv(OUT_2_3, dtype={"지역코드": str, "계약월": int})
    df_apt["거래금액"] = df_apt["거래금액"].str.replace(",", "")
    df_apt = df_apt.astype({"전용면적": float, "거래금액": int})
    df_apt["면적당금액"] = df_apt["거래금액"] / df_apt["전용면적"]

    # 2. 상반기/하반기 데이터 분리
    df_h1 = df_apt[df_apt["계약월"] <= 10]
    df_h2 = df_apt[df_apt["계약월"] > 10]

    # 3. 기간별 평균 가격 계산
    s_price_h1 = df_h1.groupby("지역코드")["면적당금액"].mean()
    s_price_h2 = df_h2.groupby("지역코드")["면적당금액"].mean()

    # 4. 가격 변동률 계산
    df_price_change = pd.merge(
        s_price_h1.rename("price_h1"),
        s_price_h2.rename("price_h2"),
        on="지역코드",
        how="outer",
    ).reset_index()

    df_price_change["price_change_pct"] = (
        (df_price_change["price_h2"] - df_price_change["price_h1"]) / df_price_change["price_h1"]
    ) * 100
    # NaN 값은 0으로 처리 (한 기간에만 거래가 있는 경우)
    df_price_change = df_price_change.fillna(0)

    # 5. 주소 및 지리 데이터 병합
    df_sido_sgg = pd.read_csv(OUT_2_1, dtype={"sido_sgg": str})
    gdf_geo = gpd.read_file(OUT_3_2, encoding="utf-8")

    df_merged = pd.merge(df_sido_sgg, df_price_change, left_on="sido_sgg", right_on="지역코드", how="inner")
    gdf_final = pd.merge(gdf_geo, df_merged, left_on="adm_nm", right_on="locatadd_nm", how="inner")

    # 6. 시각화
    sns.set_theme(context="poster", font="Malgun Gothic")
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)

    # 변동률의 최대/최소 절대값으로 컬러맵 범위 대칭 설정
    vmax = gdf_final["price_change_pct"].abs().max()
    vmin = -vmax

    gdf_final.plot(
        column="price_change_pct",
        cmap="RdBu_r",  # 상승은 파란색, 하락은 빨간색 계열
        edgecolor="k",
        legend=True,
        legend_kwds={"label": "가격 변동률 (%)", "orientation": "vertical"},
        ax=ax,
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_axis_off()
    ax.set_title("서울시 아파트 가격 변동률(2024.1~2025.8)")
    fig.set_layout_engine("tight")
    fig.savefig(OUT_3_6)


if __name__ == "__main__":
    price_change_to_img()
    print(f"가격 변동률 시각화가 완료되어 '{OUT_3_6}' 파일로 저장되었습니다.")
