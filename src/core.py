from bs4 import BeautifulSoup
from itertools import zip_longest
import sys

from .jsonio import STATUS_PATH, read_json, write_json
from .connection import get, get_with_session, post_with_session, authenticate
from .generator import (
    generate_hidden_params, 
    generate_project_info,
    generate_issues,
    find_board_id
)

BASE_URL = "https://etrack.timedia.co.jp/EasyTracker/"

PRE_POST_PARAMS = [
    "_ctl0:ContentPlaceHolder1:input_status",
    "_ctl0:ContentPlaceHolder1:input_priority",
    "_ctl0:ContentPlaceHolder1:input_category",
    "_ctl0:ContentPlaceHolder1:input_type",
    "_ctl0:ContentPlaceHolder1:input_is_readonly",
    "_ctl0:ContentPlaceHolder1:input_secret_level",
]
POST_PARAMS = [
    "_ctl0:ContentPlaceHolder1:hidden_board_id",
    "_ctl0:ContentPlaceHolder1:input_title",
    "_ctl0:ContentPlaceHolder1:input_assign_id",
    "_ctl0:ContentPlaceHolder1:response_memo",
    "_ctl0:ContentPlaceHolder1:input_target_date",
    "_ctl0:ContentPlaceHolder1:input_send_remainder_mail",
]
POST_FILE_PARAMS = [
    "_ctl0:ContentPlaceHolder1:attach_filename",
    "_ctl0:ContentPlaceHolder1:attach_filename2",
    "_ctl0:ContentPlaceHolder1:attach_filename3",
    "_ctl0:ContentPlaceHolder1:attach_filename4",
    "_ctl0:ContentPlaceHolder1:attach_filename5",
]

def __board_id_validation(html):
    INVALID_MESSAGE = "指定されたプロジェクトは存在しません"
    if html.find(INVALID_MESSAGE) > -1:
        print(INVALID_MESSAGE)
        sys.exit("プロジェクトを指定し直してください")

def setup():
    data = {
        'paramators': {
            'board_id': 'initialized'
        },
        'session': {
            'ASP.NET_SessionId': 'initialized'
        }
    }
    write_json(data, STATUS_PATH)


def login(user_id, password):
    URL = BASE_URL + "Login.aspx"

    html = get(URL)

    data = generate_hidden_params(html, request="LOGIN")
    data["textBoxId"] = user_id
    data["textBoxPassword"] = password

    authenticate(URL, data)

    print(f"ログインしました ID: {user_id}")


def list_projects():
    URL = BASE_URL + "main/MyPage.aspx"

    html = get_with_session(URL)

    project_info = generate_project_info(html)

    for (group, name) in project_info:
        print(f"{name}@{group}")


def select_project(name):
    url = BASE_URL + "main/MyPage.aspx"

    html = get_with_session(url)
    board_id = find_board_id(html, name)

    status = read_json(STATUS_PATH)
    status["paramators"]["board_id"] = board_id
    write_json(status, STATUS_PATH)

    list_issues(board_id=board_id)


def list_issues(board_id=None):
    if board_id is None:
        status = read_json(STATUS_PATH)
        board_id = status["paramators"]["board_id"]

    URL = BASE_URL + f"board/IssueList.aspx?board_id={board_id}"

    html = get_with_session(URL)
    __board_id_validation(html)

    issues = generate_issues(html)

    for no, name, status_, priority, type_, category, asign in issues:
        print(f"No. {no}: {name}\nステータス: {status_}, 重要度: {priority}, タイプ: {type_}, アサイン: {asign}")


def post_issue(title, text, status="未着手", priority=1, category="デフォルト",
    type_="タスク", readonly="", secret="on", assign_id="", date="", remainder_mail=""):
    """
    argments:

    title: str -> issue's title
    text: str -> issue's subject text
    status: str -> issue's status ["未着手", "着手", "完了"]
    priority: str -> issue's priority {"1": "普通", "2": "緊急"}
    category: str -> issue's category ["デフォルト"]
    type_: str -> issue's type ["タスク", "依頼", "バグ", "議事録", "連絡", "文書", "議論"]
    readonly: str -> commentable? {"on": False, "*": True}
    secret: str -> visiable for guest account? {"on": False, "*": True}
    assign_id: str -> assigned account's id 
    date: str -> issue's limit
    remainder_mail: str -> notificate by email to team membaers
    """

    status_ = read_json(STATUS_PATH)
    board_id = status_["paramators"]["board_id"]

    PRE_URL = BASE_URL + f"Board/AddIssuePre.aspx?board_id={board_id}"

    pre_html = get_with_session(PRE_URL)
    __board_id_validation(pre_html)
    data = generate_hidden_params(pre_html)

    pre_post_data = [status, priority, category, type_, readonly, secret]
    for param, d in zip_longest(PRE_POST_PARAMS, pre_post_data):
        data[param] = d

    html = post_with_session(PRE_URL, data=data)

    POST_URL = BASE_URL + f"Board/AddIssue.aspx?board_id={board_id}"

    data.update(generate_hidden_params(html))

    post_data = [board_id, title, assign_id, text, date, remainder_mail]
    for param, d in zip_longest(POST_PARAMS, post_data):
        data[param] = d

    files = {}
    for param in POST_FILE_PARAMS:
        files[param] = ("", "", "application/octet-stream")

    post_with_session(POST_URL, data=data, files=files)
    list_issues(board_id=board_id)
