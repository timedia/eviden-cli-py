import requests
import sys

from .jsonio import read_cookie, write_cookie

AUTH_INVALID_MESSAGE = "ログインID、メールアドレスもしくはパスワードが間違っています"
AUTH_PROPARTY_EMPTY_MESSAGE = "ログインIDかメールアドレス、パスワードを入力してください"
AUTH_SESSION_DISCONNECT_MESSAGE = "セッション切れです"

session = requests.session()

def check_request_success(html):
    if (
        html.find(AUTH_INVALID_MESSAGE) > -1
        or html.find(AUTH_PROPARTY_EMPTY_MESSAGE) > -1
        or html.find(AUTH_SESSION_DISCONNECT_MESSAGE) > -1
    ):
        sys.exit(AUTH_INVALID_MESSAGE + ".ログインし直してください.")


def get_with_session(url):
    cookies = read_cookie()
    res = session.get(url, cookies=cookies)
    check_request_success(res.text)
    return res.text


def get(url):
    res = session.get(url)
    return res.text


def post_with_session(url, data=None, files=None):
    cookies = read_cookie()
    res = session.post(url, data=data, files=files, cookies=cookies)
    check_request_success(res.text)
    return res.text


def authenticate(url, param, files=None):
    res = session.post(url, data=param, files=files)
    check_request_success(res.text)

    cookie = session.cookies.get("ASP.NET_SessionId")
    session_id = {"ASP.NET_SessionId": f"{cookie}"}

    write_cookie(session_id)
