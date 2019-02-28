import requests
from bs4 import BeautifulSoup
import sys

from jsonio import read_json, write_json, STATUS_PATH
from datastore import login_data

BASE_URL = "https://etrack.timedia.co.jp/EasyTracker/"
session = requests.session()

AUTH_INVALID_MESSAGE = "ログインID、メールアドレスもしくはパスワードが間違っています"

def login(user_id, password):
    PATH = "Login.aspx"

    status = read_json(STATUS_PATH)
    params = status["paramators"]["login"]
    print(params)
    params["textBoxId"] = user_id
    params["textBoxPassword"] = password

    res = session.post(BASE_URL+PATH, data=params)
    if res.text.find(AUTH_INVALID_MESSAGE) > -1:
        sys.exit(AUTH_INVALID_MESSAGE)

    cookie = session.cookies.get("ASP.NET_SessionId")
    session_id = {"ASP.NET_SessionId": f"{cookie}"}
    status["session"] = session_id

    status["login"]["userid"] = user_id
    status["login"]["password"] = password

    write_json(status, STATUS_PATH)

    print(f"ログインしました ID: {user_id}")

def get_html_with_session(path):
    status = read_json(STATUS_PATH)
    cookies = status["session"]

    res = session.get(BASE_URL+path, cookies=cookies)
    if res.text.find(AUTH_INVALID_MESSAGE) > -1:
        sys.exit(AUTH_INVALID_MESSAGE)
    return res.text

def genarate_project_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]
    project_info = [list(map(lambda td: td.text, row.find_all("td")[0:2])) for row in rows]

    return project_info

def list_project():
    PATH = "main/MyPage.aspx"

    html = get_html_with_session(PATH)
    project_info = genarate_project_info(html)

    for (group, name) in project_info:
        print(f"{name}@{group}")

def get_selected_project_path(html, name):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]

    for row in rows:
        project_name = row.find_all("td")[1] 
        if project_name.text == name:
            return project_name.a.get("href")[3:]

def select_project(name):
    MYPAGE_PATH = "main/MyPage.aspx"
    mypage_html = get_html_with_session(MYPAGE_PATH)

    project_path = get_selected_project_path(mypage_html, name)
    project_html = get_html_with_session(project_path)

    print(project_html)
    #soup = BeautifulSoup(project_html, 'html.parser')


if __name__=="__main__":
    # test

    # コマンドライン引数でtry-exceptするべき
    command = "--select" 

    # 引数のvalidationをしてから実行？
    if command == "--login":
        userid, password = login_data["user_id"], login_data["password"] # DEBUG
        login(userid, password)
    elif command == "--list":
        list_project()
    elif command == "--select":
        name = "自動化テスト" # DEBUG
        select_project(name)
