import json
from pathlib import Path
from playwright.sync_api import Page
from step_1_1 import OUT_DIR
from step_1_2 import run_playwright

OUT_1_3=OUT_DIR/f"{Path(__file__).stem}.json"

def goto_market_cap(page:Page):
    page.goto("https://finance.naver.com")
    page.get_by_role("link",name="국내증시").click()
    page.get_by_role("link",name="시가총액",exact=True).first.click() # 원본과 다른 코드 

def parse_table_kospi(page:Page) -> tuple[list,list]:
    tag_table=page.locator("table",has_text="코스피")
    tag_thead=tag_table.locator("thead > tr > th")
    header=tag_thead.all_inner_texts()
    tag_tbody=tag_table.locator("tbody>tr")
    body=[tr.locator("td").all_inner_texts() for tr in tag_tbody.all()]
    return header,body

if __name__=="__main__":
    play,browser,page=run_playwright(slow_mo=1000)
    goto_market_cap(page)
    header,body=parse_table_kospi(page)
    dumped=json.dumps(dict(header=header,body=body),ensure_ascii=False,indent=2)
    OUT_1_3.write_text(dumped,encoding="utf-8")
    browser.close()
    play.stop()