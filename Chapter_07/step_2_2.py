from pathlib import Path
import pandas as pd
from playwright.sync_api import Page
from step_1_1 import OUT_DIR
from step_1_2 import run_playwright
from step_1_3 import goto_market_cap,parse_table_kospi
from step_1_4 import table_to_dataframe
from step_2_1 import fetch_total_page

OUT_2_2=OUT_DIR/f"{Path(__file__).stem}.csv"

def goto_page(page:Page,to:int):
    page.goto(f"https://finance.naver.com/sise/sise_market_sum.naver?&page={to}")

def fetch_market_cap(page:Page)->pd.DataFrame:
    total_page=fetch_total_page(page)
    result=[]
    for to in range(1,total_page+1):
        goto_page(page,to)
        header,body=parse_table_kospi(page)
        df_raw=table_to_dataframe(header,body)
        result.append(df_raw)
    return pd.concat(result)

if __name__=="__main__":
    play,browser,page=run_playwright(slow_mo=1000)
    goto_market_cap(page)
    df_result=fetch_market_cap(page)
    df_result.to_csv(OUT_2_2,index=False)
    browser.close()
    play.stop()

    