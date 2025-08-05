import matplotlib.pyplot as plt
import pandas as pd

from step_1_1 import IMG_DIR  
from step_2_1 import OUT_2_1


def indicators_to_png():
    with pd.ExcelFile(OUT_2_1) as xlsx:  
        for sheet_name in xlsx.sheet_names:
            df_raw = pd.read_excel(xlsx, sheet_name=sheet_name)  
            df_raw = df_raw.tail(24)  

            x_value = df_raw.index  
            y_value = df_raw["DATA_VALUE"]  
            y_min = y_value.min()  
            change = y_value.iloc[-1] - y_value.iloc[0]  
            color = "red" if change > 0 else "blue" if change < 0 else "black"

            fig, ax = plt.subplots(figsize=(9, 3), dpi=100)  
            ax.plot(x_value, y_value, color=color, linewidth=3) 
            ax.fill_between(x_value, y_value, y_min, color=color, alpha=0.10)  
            ax.set_axis_off()  
            fig.set_layout_engine("tight") 
            fig.savefig(IMG_DIR / f"{sheet_name}.png")  


if __name__ == "__main__":
    indicators_to_png()  