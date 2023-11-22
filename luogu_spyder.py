import os
from time import sleep
import ddddocr
from urllib.parse import urljoin, urlencode

from playwright.sync_api import Playwright, sync_playwright, expect,Page
import yaml


# 设置环境变量，不让驱动下到c盘
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "driver")



# 识别登陆时的验证码
def captcha_img2txt(page,selector):
    # 获取验证码图片元素
    image_element = page.query_selector(selector)
    # 获取验证码图片的位置和尺寸
    image_box = image_element.bounding_box()
    # 截取验证码图片
    screenshot = page.screenshot(clip=image_box)
    # 将截取的图片保存到本地
    ocr = ddddocr.DdddOcr(show_ad=False)
    txt = ocr.classification(screenshot)
    return txt

def get_url(base_url,params:dict)->str:
    return urljoin(base_url, '?' + urlencode(params))


def login(url,page:Page):
    page.goto(url)
    with open('config.yaml', 'r') as file:
        data = yaml.safe_load(file)
        user = data.get('luogu')
    page.get_by_role("textbox", name="用户名、手机号或电子邮箱").fill(user['email'])
    page.get_by_role("textbox", name="密码").fill(user['pwd'])
    while True:
        captcha_txt = captcha_img2txt(page,"#app > div.main-container > main > div > div > div > div > div > div > div:nth-child(3) > div > div.img > img")
        page.get_by_role("textbox", name="右侧图形验证码").fill(captcha_txt)
        # page.once()
        page.get_by_role("button", name="登录").click()
        # 等待登录的响应
        with page.expect_response('https://www.luogu.com.cn/api/auth/userPassLogin') as response_info:
            response = response_info.value
        print(response.status)
        if response.status == 200:
            break
        else:
            # 叉掉提示
            page.get_by_role("button", name="OK").click()
            # 刷新验证码
            # page.get_by_role("main").locator("img").nth(1).click()
    # 自动跳转到了主页即登陆成功
    page.wait_for_url('https://www.luogu.com.cn/')

def get_records(page:Page,user_id,last_updatetime:str=None):
    page_num=1
    # 先跳一下拿到总页数
    record_url = get_url('https://www.luogu.com.cn/record/list',{'user':user_id,'page':page_num})
    page.goto(record_url)
    total_submmit_num = page.query_selector("#app > div.main-container > main > div > section > div > div > span > span").inner_text()
    total_submmit_num = int(total_submmit_num)
    total_page_num = page.query_selector('#app > div.main-container > main > div > div > div > div.bottom > div > div > span > strong')
    if total_page_num is None:
        total_page_num = 1
    else:
        total_page_num = int(total_page_num.inner_text())
    records = []
    # 遍历每一页
    while page_num <= total_page_num:
        record_url = get_url('https://www.luogu.com.cn/record/list',{'user':user_id,'page':page_num})
        page.goto(record_url)
        # 开始收集
        _records = page.query_selector_all('#app > div.main-container > main > div > div > div > div.border.table > div > div')
        for record in _records:
            submit_time = record.query_selector('div.user > div > span.lfe-caption').text_content().replace("\n","").strip()
            # 不去找上次已经爬过的记录了
            if last_updatetime and last_updatetime <= submit_time:
                page_num = total_page_num +1
                break
            submit_status = record.query_selector('div.status > a > span.lfe-caption.tag.status-name').text_content().replace("\n","").strip()
            submit_question = record.query_selector('div.problem > div > a').text_content().replace("\n","").replace(" ","")
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
        login("https://www.luogu.com.cn/auth/login",page)
        for user_id in users:
            record_msg = get_records(page,user_id)
            print(user_id,record_msg['total_submmit_num'])
        context.close()
        browser.close()


if __name__ == "__main__":
    users = ['473282','473279']
    main(users)