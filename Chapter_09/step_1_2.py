import os
import requests
from dotenv import load_dotenv

load_dotenv()

ECOS_KEY = os.getenv("ECOS_KEY")

resp=requests.get(f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/10/722Y001/A/2020/2023/0101000/?/?/?")
resp.json()