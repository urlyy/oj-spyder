import os
import re
from time import sleep
from urllib.parse import urljoin, urlencode

from playwright.sync_api import Playwright, sync_playwright, expect,Page,Response,Route,Request

import yaml



# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")


# def get_records(page:Page,user_id,page_num=1,last_updatetime:str=None):
#     # 先跳一下拿到总页数
#     record_url = f'https://leetcode.cn/u/{user_id}/'
#     page.goto(record_url)
#     total_submmit_num = page.query_selector("#app > div.main-container > main > div > section > div > div > span > span").text_content()
#     total_submmit_num = int(total_submmit_num)
#     total_page_num = page.query_selector('#app > div.main-container > main > div > div > div > div.bottom > div > div > span > strong').text_content()
#     total_page_num = int(total_page_num)
#     records = []
#     # 遍历每一页
#     while page_num <= total_page_num:
#         record_url = get_url('https://www.luogu.com.cn/record/list',{'user':user_id,'page':page_num})
#         page.goto(record_url)
#         # 开始收集
#         _records = page.query_selector_all('#app > div.main-container > main > div > div > div > div.border.table > div > div')
#         for record in _records:
#             submit_time = record.query_selector('div.user > div > span.lfe-caption').text_content().replace("\n","").strip()
#             # 不去找上次已经爬过的记录了
#             if last_updatetime and last_updatetime <= submit_time:
#                 page_num = total_page_num +1
#                 break
#             submit_status = record.query_selector('div.status > a > span.lfe-caption.tag.status-name').text_content().replace("\n","").strip()
#             submit_question = record.query_selector('div.problem > div > a').text_content().replace("\n","").replace(" ","")
#             records.append({
#                 "submit_time":submit_time,
#                 "submit_status":submit_status,
#                 "submit_question":submit_question
#             })
#         page_num += 1
#     return {"total_submmit_num":total_submmit_num,"records":records}
    
    
class User:
    def __init__(self,username,phoneOrEmail,pwd) -> None:
        self.username = username
        self.phoneOrEmail = phoneOrEmail
        self.pwd = pwd
    def __str__(self) -> str:
        return "{" +f"username:{self.username},phoneOrEmail:{self.phoneOrEmail}" +  "}"

def login(page:Page,user:User):
    print(user)
    page.goto("https://leetcode.cn/accounts/login/?next=%2F")
    page.get_by_text("帐号密码登录").click()
    page.get_by_placeholder("手机/邮箱").fill(user.phoneOrEmail)
    page.get_by_placeholder("输入密码").fill(user.pwd)
    sleep(1)
    page.get_by_role("button", name="登录").click()
    with page.expect_response('https://leetcode.cn/graphql/') as response_info:
        response = response_info.value
    # if response.status == 200:
    #     break
    # else:
    
    

# 爬到所有已通过的题目
def get_records(page:Page,last_updatetime=None):
    # 两个线程通信
    _records = None
    def handle_request(route:Route,req:Request):
        if req.method == 'POST' and req.url.find('graphql') != -1:
            # 获取请求的内容
            request_payload = req.post_data
            print('GraphQL 请求:', req.response())
            # 继续处理请求
            route.continue_()
        else:
            # 其他请求不做处理，继续请求
            route.continue_()
    page.route('**', lambda route, request: handle_request(route, request))
    def handle_response(resp:Response):
        global _records
        # print(" "*20+resp.url)
        if resp.url.find('graphql') != -1:
            data:dict = resp.json()['data']
            if "userProfileQuestions" in data.keys():
                # print("近来了")
                _records = data["userProfileQuestions"]["questions"]
    page.on("response",handle_response)
    page.goto('https://leetcode.cn/progress/')
    page.wait_for_selector('.highcharts-root')
    number_wrapper = page.query_selector('div[class*="NumbersWrapper"]')
    ac_num = number_wrapper.query_selector('div:nth-child(1)').inner_text()
    # submit_no_ac_num = number_wrapper.query_selector('div:nth-child(2)')
    # no_write_number_wrapper.query_selector('div:nth-child(3)')
    total_submit_num = number_wrapper.query_selector('div:nth-child(4)').inner_text()
    submit_ac_num = number_wrapper.query_selector('div:nth-child(5)').inner_text()
    # 提交通过率 = number_wrapper.query_selector('div:nth-child(5)')
    records = []
    finish = False
    pagination = page.query_selector('div[class*="PaginationWrapper"] > div')
    page_num = 1
    _records = []
    def check_handle_response(resp:Response):
        if resp.url.find('graphql') != -1:
            data:dict = resp.json()['data']
            if "userProfileQuestions" in data.keys():
                _records = data["userProfileQuestions"]["questions"]
                return True
        return False
    while not finish:
        # 空转等待另一个线程获得response
        while _records is None:
            pass
        print(f"当前在{page_num}页")
        # page.expect_response(check_handle_response)
        # _records = page.query_selector_all('.ant-table-tbody > tr')
        for record in _records:
            # submit_question = record.query_selector('td:nth-child(3)').inner_text()
            # submit_status = record.query_selector('td:nth-child(4)').inner_text()
            # submit_time = record.query_selector('td:nth-child(2)').inner_text()
            submit_question = record['translatedTitle']
            # 只爬了通过了的
            submit_status = 'Accepeted'
            difficulty = record['difficulty']
            submit_time = record['lastSubmittedAt']
            # 避免获取上次已经爬完了的
            if last_updatetime and last_updatetime <= submit_time:
                finish = True
                break
            records.append({
                "submit_time":submit_time,
                "submit_status":submit_status,
                "submit_question":submit_question,
                "difficulty":difficulty
            })
        _records = None
        # page.remove_listener("response", handle_response)
        # page.on("response", handle_response)
        last_button = pagination.query_selector('button:nth-last-child(2)')
        if last_button.inner_text() == str(page_num):
            break
        page_num += 1
        page.on("response",handle_response)
        next_button = pagination.query_selector('button:last-child')
        next_button.click()
    return {"records":records,"profile":{"ac_num":ac_num,"total_submit_num":total_submit_num,"submit_ac_num":submit_ac_num}}
        
    
    
def main(users):
    p = sync_playwright().start()
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()
    for user in users:
        login(page,user)
        records_msg = get_records(page)
        print(len(records_msg['records']))
    browser.close()
    p.stop()

if __name__ == "__main__":
    # 读取 YAML 文件
    with open('config.yaml', 'r') as file:
        data = yaml.safe_load(file)
        user = data.get('leetcode')
    users = [User(user["username"],user['phoneOrEmail'],user['pwd'])]
    main(users)