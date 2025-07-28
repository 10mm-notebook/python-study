from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from step_1_1 import OUT_DIR
from step_2_2 import OUT_2_2

# 파일 경로와 확장자 확인
print(OUT_2_2)
print(Path(OUT_2_2).suffix)

df_raw=pd.read_excel(OUT_2_2,sheet_name="코스피지수",dtype="string")
df_raw["TIME"]=pd.to_datetime(df_raw["TIME"],format="%Y%m%d")
df_raw["DATA_VALUE"]=df_raw["DATA_VALUE"].astype(float)



sns.set_theme(context="poster",style="whitegrid",font="Malgun Gothic")
sns.set_style({"grid.linestyle": ":","grid.color": "#CCCCCC"})

fig,ax=plt.subplots(figsize=(16,9),dpi=100)
sns.lineplot(data=df_raw,x="TIME",y="DATA_VALUE",ax=ax)
sns.despine(top=True,right=True)

ax.set_title("코스피지수")
ax.set_xlabel("날짜")
ax.set_ylabel("지수")
fig.set_layout_engine("tight")
fig.savefig(OUT_DIR/f"{Path(__file__).stem}.png")