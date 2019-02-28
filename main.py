import requests
from bs4 import BeautifulSoup
import sys

from jsonio import read_json, write_json, STATUS_PATH
from datastore import login_data

BASE_URL = "https://etrack.timedia.co.jp/EasyTracker/"
session = requests.session()

AUTH_INVALID_MESSAGE = "ログインID、メールアドレスもしくはパスワードが間違っています"
AUTH_PROPARTY_EMPTY_MESSAGE = "ログインIDかメールアドレス、パスワードを入力してください"

def __check_login_success(html):
    if html.find(AUTH_INVALID_MESSAGE) > -1 or html.find(AUTH_PROPARTY_EMPTY_MESSAGE) > -1:
        sys.exit(AUTH_INVALID_MESSAGE+".ログインし直してください.")

def login(user_id, password):
    PATH = "Login.aspx"

    status = read_json(STATUS_PATH)
    params = status["paramators"]["login"]
    params["textBoxId"] = user_id
    params["textBoxPassword"] = password

    res = session.post(BASE_URL+PATH, data=params)
    __check_login_success(res.text)

    cookie = session.cookies.get("ASP.NET_SessionId")
    session_id = {"ASP.NET_SessionId": f"{cookie}"}
    status["session"] = session_id

    status["login"]["userid"] = user_id
    status["login"]["password"] = password

    write_json(status, STATUS_PATH)

    print(f"ログインしました ID: {user_id}")

def __generate_html_with_session(path):
    status = read_json(STATUS_PATH)
    cookies = status["session"]

    res = session.get(BASE_URL+path, cookies=cookies)
    __check_login_success(res.text)
    return res.text

def __generate_project_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]
    project_info = [list(map(lambda td: td.text, row.find_all("td")[:2])) for row in rows]

    return project_info

def list_projects():
    PATH = "main/MyPage.aspx"

    html = __generate_html_with_session(PATH)
    project_info = __generate_project_info(html)

    for (group, name) in project_info:
        print(f"{name}@{group}")

def __generate_selected_project_path(html, name):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]

    for row in rows:
        project_name = row.find_all("td")[1] 
        if project_name.text == name:
            return project_name.a.get("href")[3:]
    
    sys.exit("selected project does not exist")

def __generate_issues(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[2:-1]
    issues = [list(map(lambda td: td.text, row.find_all("td")[:7])) for row in rows]

    return issues

def select_project(name):
    MYPAGE_PATH = "main/MyPage.aspx"
    mypage_html = __generate_html_with_session(MYPAGE_PATH)
    project_path = __generate_selected_project_path(mypage_html, name)

    status = read_json(STATUS_PATH)
    status["paramators"]["select"]["name"] = name
    status["paramators"]["select"]["path"] = project_path
    write_json(status, STATUS_PATH)

    project_html = __generate_html_with_session(project_path)
    issues = __generate_issues(project_html)

    for no, name, status_, priority, type_, category, asign in issues:
        print(f"No. {no}: {name}\nステータス: {status_}, 重要度: {priority}, タイプ: {type_}, アサイン: {asign}")

def list_issues():
    status = read_json(STATUS_PATH) 
    project_path = status["paramators"]["select"]["path"]

    project_html = __generate_html_with_session(project_path)
    issues = __generate_issues(project_html)

    for no, name, status_, priority, type_, category, asign in issues:
        print(f"No. {no}: {name}\nステータス: {status_}, 重要度: {priority}, タイプ: {type_}, アサイン: {asign}")


if __name__=="__main__":
    # test

    # コマンドライン引数でtry-exceptするべき
    command = "--login" 

    # 引数のvalidationをしてから実行？
    if command == "--login":
        userid, password = login_data["user_id"], login_data["password"] # DEBUG
        login(userid, password)
    elif command == "--list":
        list_projects()
    elif command == "--select":
        name = "自動化テスト" # DEBUG
        select_project(name)
    elif command == "--issues":
        list_issues()
