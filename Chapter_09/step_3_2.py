from pathlib import Path

import pandas as pd
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from step_1_1 import OUT_DIR
from step_2_2 import OUT_2_2

sns.set_theme(context="poster",style="whitegrid",font="Malgun Gothic")
sns.set_style({"grid.linestyele": ":", "grid.color":"#CCCCCC"})

fig,axes = plt.subplots(figsize=(16,9),dpi=100,nrows=2,ncols=2)
sheet_names=[["국고채","회사채"],["코스피지수","원달러환율"]]

for idx_row,row in enumerate(sheet_names):
    for idx_col,name in enumerate(row):
        df_raw=pd.read_excel(OUT_2_2,sheet_name=name,dtype="string")
        df_raw["TIME"]=pd.to_datetime(df_raw["TIME"],format="%Y%m%d")
        df_raw["DATA_VALUE"]=df_raw["DATA_VALUE"].astype(float)
        df_tail = df_raw.tail(100)

        ax: Axes = axes[idx_row][idx_col]
        sns.lineplot(data=df_tail,x="TIME",y="DATA_VALUE",ax=ax)
        sns.despine(top=True,right=True,bottom=True,left=True)

        ax.set_title(name)
        ax.xaxis.set_visible(False)
        ax.set_ylabel(None)
        ax.set_facecolor("#EEEEEE")

fig.set_layout_engine("tight")
fig.savefig(OUT_DIR/f"{Path(__file__).stem}.png")