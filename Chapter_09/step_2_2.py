from pathlib import Path
import pandas as pd
from datakart import Ecos

from step_1_1 import OUT_DIR

OUT_2_2=OUT_DIR / f"{Path(__file__).stem}.xlsx"

import os
from dotenv import load_dotenv

load_dotenv()

def ecos_to_xlsx():
    ECOS_KEY = os.getenv("ECOS_KEY")
    CODE_LIST = [
        ["기준금리", "722Y001", "D", "0101000", 1000],
        ["국고채", "817Y002", "D", "010200000", 1000],
        ["회사채", "817Y002", "D", "010300000", 1000],
        ["코스피지수", "802Y001", "D", "0001000", 1000],
        ["원달러환율", "731Y001", "D", "0000001", 1000],
    ]

    with pd.ExcelWriter(OUT_2_2) as writer:
        ecos=Ecos(ECOS_KEY)
        for name, stat_code,freq, item_code1, limit in CODE_LIST:
            resp=ecos.stat_search(
                stat_code=stat_code,
                freq=freq,
                item_code1=item_code1,
                limit=limit,
            )
            df_raw=pd.DataFrame(resp)
            df_raw.to_excel(writer,sheet_name=name,index=False)

if __name__=="__main__":
    ecos_to_xlsx()     