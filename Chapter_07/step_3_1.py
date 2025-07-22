from pathlib import Path
import pandas as pd
from step_1_1 import OUT_DIR
from step_2_2 import OUT_2_2
OUT_3_1=OUT_DIR/f"{Path(__file__).stem}.csv"
def top_kospi_company(df_raw:pd.DataFrame,prop:float)->pd.DataFrame:
    df_raw["시가총액"]=df_raw["시가총액"].str.replace(",","").astype(int)
    df_raw["조단위"]=df_raw["시가총액"]/10_000
    df_raw=df_raw.sort_values("시가총액",ascending=False)
    df_raw["누적비율"]=df_raw["시가총액"].cumsum()/df_raw["시가총액"].sum()
    df_sliced=df_raw.loc[df_raw["누적비율"]<=prop]
    return df_sliced.filter(["종목명","시가총액","조단위","누적비율"])

if __name__ == "__main__":
    df_raw=pd.read_csv(OUT_2_2)
    df_top=top_kospi_company(df_raw,0.5)
    df_top.to_csv(OUT_3_1,index=False)