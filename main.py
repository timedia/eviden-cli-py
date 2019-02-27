import requests
from bs4 import BeautifulSoup
import sys

from jsonio import read_json, write_json, STATUS_PATH
from setting import LoginData

BASE_URL = "https://etrack.timedia.co.jp/EasyTracker/"
session = requests.session()

AUTH_INVALID_MESSAGE = "ログインID、メールアドレスもしくはパスワードが間違っています"

def login(user_id, password):
    PATH = "Login.aspx"

    status = read_json(STATUS_PATH)
    params = {
        '__VIEWSTATE': status["paramators"]["login"]["__VIEWSTATE"],
        '__VIEWSTATEGENERATOR': status["paramators"]["login"]["__VIEWSTATEGENERATOR"],
        '__EVENTVALIDATION': status["paramators"]["login"]["__EVENTVALIDATION"],
        'textBoxId': user_id,
        'textBoxPassword': password,
        'buttonLogin': 'ログイン'
    }

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

    name_and_path = {row.find_all("td")[1].text: row.find_all("td")[1].a.get("href")[3:] for row in rows}
    return name_and_path[name]

def select_project(name):
    MYPAGE_PATH = "main/MyPage.aspx"
    mypage_html = get_html_with_session(MYPAGE_PATH)

    project_path = get_selected_project_path(mypage_html, name)
    project_html = get_html_with_session(project_path)

    print(project_html)

if __name__=="__main__":
    # コマンドライン引数でtry-exceptするべき
    command = "--select" # sys.argv[1]

    # 引数のvalidationをしてから実行？
    if command == "--login":
        ld = LoginData()
        userid, password = ld.user_id, ld.password # DEBUG
        login(userid, password)
    elif command == "--list":
        list_project()
    elif command == "--select":
        name = "自動化テスト" # DEBUG
        select_project(name)
