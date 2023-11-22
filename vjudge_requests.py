import os
import requests
from bs4 import BeautifulSoup
import datetime  
from playwright.sync_api import Playwright, sync_playwright, expect,Page


# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")

def format_timestamp(timestamp)->str:
    timestamp /= 1000
    dt_object = datetime.datetime.fromtimestamp(timestamp)  
    # 自定义格式  
    formatted = dt_object.strftime('%Y-%m-%d %H:%M:%S')  
    return formatted

def get_records(user_id,last_updatetime=None):
    page_num = 1
    records = []
    while True:
        page_size = 20
        start = (page_num-1)*page_size
        url = f'https://vjudge.net/status/data?draw=3&start={start}&length={page_size}&un={user_id}&OJId=All&probNum=&res=0&language=&onlyFollowee=false&orderBy=run_id&_=1700596952140'
        resp = requests.get(url)
        data = resp.json()['data']
        print(page_num,len(data))
        if len(data)==0:
            break
        for record in data:
            oj = record['oj']
            id = record['probNum']
            submit_question = f"{oj}-{id}"
            submit_status = record['status']
            submit_time = format_timestamp(record['time'])
            # 避免获取上次已经爬完了的
            if last_updatetime and last_updatetime <= submit_time:
                finish = True
                break
            records.append({
                "submit_time":submit_time,
                "submit_status":submit_status,
                "submit_question":submit_question
            })
        page_num += 1
    return records



def get_profile(page:Page,user_id):
    profile_url = f"https://vjudge.net/user/{user_id}"
    page.goto(profile_url)
    overall_solved = page.query_selector("body > div.container > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(4) > td > a").inner_text()
    overall_solved = int(overall_solved)
    overall_attempted = page.query_selector("body > div.container > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(5) > td > a").inner_text()
    overall_attempted = int(overall_attempted)
    return {"Overall solved":overall_solved,"Overall attempted":overall_attempted}



def main(users:list):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        for user_id in users:
            profile = get_profile(page,user_id)
            records = get_records(user_id)
            print(user_id,profile,len(records))
        context.close()
        browser.close()
        
if __name__ == '__main__':
    users = ['zjw2021401326','2213732736','hzw2019401243']
    main(users)