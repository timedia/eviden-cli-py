import requests
from bs4 import BeautifulSoup
import sys
from itertools import zip_longest

from jsonio import read_json, write_json, STATUS_PATH
from datastore import login_data

BASE_URL = "https://etrack.timedia.co.jp/EasyTracker/"
session = requests.session()

AUTH_INVALID_MESSAGE = "ログインID、メールアドレスもしくはパスワードが間違っています"
AUTH_PROPARTY_EMPTY_MESSAGE = "ログインIDかメールアドレス、パスワードを入力してください"

HIDDEN_PARAMS = [
    "__VIEWSTATE", 
    "__VIEWSTATEGENERATOR", 
    "__EVENTVALIDATION", 
    "_ctl0:ContentPlaceHolder1:buttonAdd"
]
PRE_POST_PARAMS = [
    "_ctl0:ContentPlaceHolder1:input_status",
    "_ctl0:ContentPlaceHolder1:input_priority",
    "_ctl0:ContentPlaceHolder1:input_category",
    "_ctl0:ContentPlaceHolder1:input_type",
    "_ctl0:ContentPlaceHolder1:input_is_readonly",
    "_ctl0:ContentPlaceHolder1:input_secret_level"
]
POST_PARAMS = [
    "_ctl0:ContentPlaceHolder1:hidden_board_id",
    "_ctl0:ContentPlaceHolder1:input_title",
    "_ctl0:ContentPlaceHolder1:input_assign_id",
    "_ctl0:ContentPlaceHolder1:response_memo",
    "_ctl0:ContentPlaceHolder1:input_target_date",
    "_ctl0:ContentPlaceHolder1:input_send_remainder_mail"
]
POST_FILE_PARAMS = [
    "_ctl0:ContentPlaceHolder1:attach_filename",
    "_ctl0:ContentPlaceHolder1:attach_filename2",
    "_ctl0:ContentPlaceHolder1:attach_filename3",
    "_ctl0:ContentPlaceHolder1:attach_filename4",
    "_ctl0:ContentPlaceHolder1:attach_filename5"
]

def __check_request_success(html):
    if html.find(AUTH_INVALID_MESSAGE) > -1 or html.find(AUTH_PROPARTY_EMPTY_MESSAGE) > -1:
        sys.exit(AUTH_INVALID_MESSAGE+".ログインし直してください.")

def login(user_id, password):
    URL = BASE_URL+"Login.aspx"

    status = read_json(STATUS_PATH)
    params = status["paramators"]["login"]
    params["textBoxId"] = user_id
    params["textBoxPassword"] = password

    res = session.post(URL, data=params)
    __check_request_success(res.text)

    cookie = session.cookies.get("ASP.NET_SessionId")
    session_id = {"ASP.NET_SessionId": f"{cookie}"}
    status["session"] = session_id

    status["paramators"]["login"]["textBoxId"] = user_id
    status["paramators"]["login"]["textBoxPassword"] = password

    write_json(status, STATUS_PATH)

    print(f"ログインしました ID: {user_id}")

def  __get_with_session(url):
    status = read_json(STATUS_PATH)
    cookies = status["session"]

    res = session.get(url, cookies=cookies)
    __check_request_success(res.text)
    return res.text

def __generate_project_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]
    project_info = [list(map(lambda td: td.text, row.find_all("td")[:2])) for row in rows]

    return project_info

def list_projects():
    url = BASE_URL+"main/MyPage.aspx"

    html =  __get_with_session(url)
    project_info = __generate_project_info(html)

    for (group, name) in project_info:
        print(f"{name}@{group}")

def __find_selected_board_id(html, name):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]

    for row in rows:
        project_name = row.find_all("td")[1] 
        if project_name.text == name:
            return project_name.a.get("href").split("=")[1]
    
    sys.exit("selected project does not exist")

def __generate_issues(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[2:-1]
    issues = [list(map(lambda td: td.text, row.find_all("td")[:7])) for row in rows]

    return issues

def __print_issues_with_board_id(board_id):
    url = BASE_URL+f"board/IssueList.aspx?board_id={board_id}"
    project_html =  __get_with_session(url)
    issues = __generate_issues(project_html)

    for no, name, status_, priority, type_, category, asign in issues:
        print(f"No. {no}: {name}\nステータス: {status_}, 重要度: {priority}, タイプ: {type_}, アサイン: {asign}")

def select_project(name):
    url = BASE_URL + "main/MyPage.aspx"
    mypage_html =  __get_with_session(url)
    board_id = __find_selected_board_id(mypage_html, name)

    status = read_json(STATUS_PATH)
    status["paramators"]["select"]["name"] = name
    status["paramators"]["select"]["path"] = board_id
    write_json(status, STATUS_PATH)

    __print_issues_with_board_id(board_id)

def list_issues():
    status = read_json(STATUS_PATH) 
    board_id = status["paramators"]["select"]["path"]

    __print_issues_with_board_id(board_id)

def __post_data_and_files(url, cookies, data, files):
    return session.post(
        url,
        data=data,
        files=files,
        cookies=cookies
    )

def __generate_hidden_params(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {s: soup.find("input", attrs={"name": s}).get("value") for s in HIDDEN_PARAMS}
    return data

def post_issue(title, text, status="未着手", priority=1, category="デフォルト", type_="タスク", readonly="", sercret_level="on", assign_id="", target_date="", remainder_mail=""):
    # status.jsonからboard_idとクッキーを取得
    status_ = read_json(STATUS_PATH)
    board_id = status_["paramators"]["select"]["path"]
    cookies = status_["session"]

    # IssueAddPre, IssueAddに対応するurlとdataの用意
    pre_url = BASE_URL + f"Board/AddIssuePre.aspx?board_id={board_id}" 
    post_url = BASE_URL + f"Board/AddIssue.aspx?board_id={board_id}"

    # Preページの__VIEWSTATEなどを取得する
    pre_html = __get_with_session(pre_url)
    __check_request_success(pre_html)
    data = __generate_hidden_params(pre_html)

    # Preページで一旦POSTしIssueAddのhtmlを取得
    pre_post_data = [status, priority, category, type_, readonly, sercret_level]
    for param, d in zip_longest(PRE_POST_PARAMS, pre_post_data):
        data[param] = d

    res = session.post(pre_url, data=data, cookies=cookies)
    html = res.text
    __check_request_success(html)

    # POST用のdataとfilesを整える
    post_data = [board_id, title, assign_id, text, target_date, remainder_mail]
    data.update(__generate_hidden_params(html))
    for param, d in zip_longest(POST_PARAMS, post_data):
        data[param] = d

    files = {}
    for param in POST_FILE_PARAMS:
        files[param] = ("", "", "application/octet-stream")

    # POST
    res = session.post(post_url, data=data, files=files, cookies=cookies)
    print(res.text)

if __name__=="__main__":
    # コマンドライン引数でtry-exceptするべき
    command = sys.argv[1]

    # 引数のvalidationをしてから実行？
    if command == "login":
        userid, password = login_data["user_id"], login_data["password"] # DEBUG
        login(userid, password)
    elif command == "list":
        list_projects()
    elif command == "select":
        name = "自動化テスト02" # DEBUG
        select_project(name)
    elif command == "issues":
        list_issues()
    elif command == "post":
        post_issue("社外秘", "社外秘の動作テスト")
