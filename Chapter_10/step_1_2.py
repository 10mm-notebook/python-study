from pathlib import Path

import pandas as pd
from datakart import Fss

from step_1_1 import OUT_DIR 

from dotenv import load_dotenv
import os

load_dotenv()

FSS_KEY=os.getenv('FSS_KEY')

OUT_1_2 = OUT_DIR / f"{Path(__file__).stem}.xlsx"


def deposit_info_to_xlsx(): 
    fss = Fss(FSS_KEY)  
    resp = fss.deposit_search(fin_grp="은행", intr_rate_type="단리", save_trm="12", join_member="제한없음")  # API 호출
    df_raw = pd.DataFrame(resp) 
    df_raw.to_excel(OUT_1_2, index=False) 


if __name__ == "__main__":
    deposit_info_to_xlsx()  