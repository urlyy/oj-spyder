import os
from time import sleep
from urllib.parse import urljoin, urlencode

from playwright.sync_api import Playwright, sync_playwright, expect,Page


# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")

def get_submissions_url(user_id,page_num):
    return f"https://codeforces.com/submissions/{user_id}/page/{page_num}"

def get_profile_url(user_id,page_num):
    return f"https://codeforces.com/profile/{user_id}/page"

def get_records(page:Page,user_id,last_updatetime:str=None):
    # 先跳一下拿到总页数
    page_num = 1
    record_url = get_submissions_url(user_id,page_num)
    page.goto(record_url)
    # total_submmit_num = page.query_selector("body > div.nk-container.acm-container > div.nk-container > div.nk-main.with-profile-menu.clearfix > section > div.my-state-main > div:nth-child(3) > div").inner_text()
    # total_submmit_num = int(total_submmit_num)
    total_submmit_num = 1
    last_page_button = page.query_selector('.pagination > ul >li:nth-last-child(2)')
    if last_page_button is None:
        total_page_num = 1
    else:
        total_page_num = int(last_page_button.inner_text())
    records = []
    while page_num <= total_page_num:
        record_url = get_submissions_url(user_id,page_num)
        page.goto(record_url)
        _records = page.query_selector_all('#pageContent > div.datatable > div:nth-child(6) > table > tbody > tr:not(:first-child)')
        for record in _records:
            submit_question = record.query_selector('td:nth-child(4)').inner_text()
            submit_status = record.query_selector('td:nth-child(6)').inner_text()
            submit_time = record.query_selector('td:nth-child(2)').inner_text()
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
    all_records = dict()
    users = ['Paper_the_boar','jsulyy','jsu-ysj']
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        for user_id in users:
            record_msg = get_records(page,user_id)
            print(user_id,record_msg['total_submmit_num'],len(record_msg['records']))
            all_records[user_id] = record_msg
        context.close()
        browser.close()
    return all_records