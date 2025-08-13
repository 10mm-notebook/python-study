import json
from pathlib import Path
import pandas as pd
from step_1_1 import OUT_DIR
from step_1_3 import OUT_1_3

def clean_white_space(text:str)->str:
    return " ".join(text.split())

def table_to_dataframe(header:list, body:list)->pd.DataFrame:
    df_raw=pd.DataFrame(body,columns=header)
    df_raw=df_raw.dropna(how="any")
    df_raw=df_raw.iloc[:,:-1]
    for col in df_raw.columns:
        df_raw[col]=df_raw[col].apply(clean_white_space)
    return df_raw

if __name__=="__main__":
    parsed=json.loads(OUT_1_3.read_text(encoding="utf-8"))
    header,body=parsed["header"],parsed["body"]
    df_raw=table_to_dataframe(header,body)
    df_raw.to_csv(OUT_DIR/f"{Path(__file__).stem}.csv",index=False)