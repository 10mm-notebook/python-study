from pathlib import Path
import pandas as pd
from datakart import Ecos

from step_1_1 import OUT_DIR

import os
from dotenv import load_dotenv

load_dotenv()

ECOS_KEY = os.getenv("ECOS_KEY")
ecos=Ecos(ECOS_KEY)
resp=ecos.stat_search(
    stat_code="722Y001",
    freq="M",
    item_code1="0101000",
    start="202301",
    end="202412",
)
df_raw=pd.DataFrame(resp)
df_raw.to_csv(OUT_DIR/f"{Path(__file__).stem}.csv",index=False)