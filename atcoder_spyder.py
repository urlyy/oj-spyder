import requests
from bs4 import BeautifulSoup

def get_records(user_id,last_updatetime=None):
    url = f'https://atcoder.jp/users/{user_id}/history'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text,'lxml')
    contests = soup.select('#history > tbody > tr')
    records = []
    for contest in contests:
        contest_time = contest.select_one('td:nth-child(1)').text
        # 只爬了通过了的
        submit_time = contest.select_one('td:nth-child(3)').text
        # 避免获取上次已经爬完了的
        if last_updatetime and last_updatetime <= submit_time:
            finish = True
            break
        records.append({
            "submit_time":submit_time,
            "contest_time":contest_time
        })
    return records

def main():
    users = ['tourist']
    all_records = dict()
    for user in users:
        records = get_records(user)
        print(records)
        all_records[user] = records
    return all_records