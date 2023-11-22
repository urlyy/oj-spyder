import requests
from bs4 import BeautifulSoup



def get_records(user_id):
    page_num = 1
    url = f"https://ac.nowcoder.com/acm/contest/profile/{user_id}/practice-coding?&pageSize=10&search=&statusTypeFilter=-1&languageCategoryFilter=-1&orderType=DESC&page={page_num}"
    response = requests.get(url)

    # 解析页面内容
    soup = BeautifulSoup(response.text, 'lxml')

    # 提取所需数据
    title = soup.title.text
    paragraphs = soup.find_all('p')
    
import os
from time import sleep
from urllib.parse import urljoin, urlencode

from playwright.sync_api import Playwright, sync_playwright, expect,Page


# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")

def get_url(user_id,page_num):
    return f"https://ac.nowcoder.com/acm/contest/profile/{user_id}/practice-coding?&pageSize=10&search=&statusTypeFilter=-1&languageCategoryFilter=-1&orderType=DESC&page={page_num}"

def get_records(page:Page,user_id,last_updatetime:str=None):
    # 先跳一下拿到总页数
    page_num = 1
    record_url = get_url(user_id,page_num)
    page.goto(record_url)
    total_submmit_num = page.query_selector("body > div.nk-container.acm-container > div.nk-container > div.nk-main.with-profile-menu.clearfix > section > div.my-state-main > div:nth-child(3) > div").inner_text()
    total_submmit_num = int(total_submmit_num)
    pagination = page.query_selector('body > div.nk-container.acm-container > div.nk-container > div.nk-main.with-profile-menu.clearfix > section > div.pagination > ul')
    if pagination is None:
        total_page_num = 1
    else:
        goto_last_page_button = page.get_by_role("link", name="末页")
        goto_last_page_button.click()
        page.wait_for_load_state()
        last_page_button = page.query_selector('body > div.nk-container.acm-container > div.nk-container > div.nk-main.with-profile-menu.clearfix > section > div.pagination > ul > li.active')
        total_page_num = int(last_page_button.inner_text())
    records = []
    if total_submmit_num != 0:
        while page_num <= total_page_num:
            record_url = get_url(user_id,page_num)
            page.goto(record_url)
            _records = page.query_selector_all('body > div.nk-container.acm-container > div.nk-container > div.nk-main.with-profile-menu.clearfix > section > table > tbody > tr')
            for record in _records:
                submit_question = record.query_selector('td:nth-child(2) > a').inner_text()
                submit_status = record.query_selector('td:nth-child(3) > a').inner_text()
                submit_time = record.query_selector('td:nth-child(9)').inner_text()
                # 避免获取上次已经爬完了的
                if last_updatetime and last_updatetime <= submit_time:
                    page_num = total_page_num +1
                    break
                records.append({
                    "submit_time":submit_time,
                    "submit_status":submit_status,
                    "submit_question":submit_question
                })
            page_num += 1
    return {"total_submmit_num":total_submmit_num,"records":records}

def main(users:list):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        for user_id in users:
            record_msg = get_records(page,user_id)
            print(user_id,record_msg['total_submmit_num'],len(record_msg['records']))
        context.close()
        browser.close()
        
if __name__ == '__main__':
    users = ['210139192','245893655','494196561','769154733']
    main(users)