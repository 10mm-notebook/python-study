from playwright.sync_api import Page
from step_1_2 import run_playwright
from step_1_3 import goto_market_cap

def fetch_total_page(page:Page)->int:
    table=page.locator("table",has_text="페이지 네비게이션")
    td=table.locator("tbody>tr>td").last
    href=td.locator("a").get_attribute("href")
    return int(href.split("=")[-1])

if __name__=="__main__":
    play,browser,page=run_playwright(slow_mo=1000)
    goto_market_cap(page)
    total_page=fetch_total_page(page)
    print(f"{total_page=}")
    browser.close()
    play.stop()