import requests
from bs4 import BeautifulSoup
import sys

from jsonio import read_json, write_json, status_path
from setting import LoginData

url = "https://etrack.timedia.co.jp/EasyTracker/"
session = requests.session()

auth_invalid_message = "ログインID、メールアドレスもしくはパスワードが間違っています"

def login(user_id, password):
    path = "Login.aspx"

    status = read_json(status_path)
    params = {
        '__VIEWSTATE': status["paramators"]["login"]["__VIEWSTATE"],
        '__VIEWSTATEGENERATOR': status["paramators"]["login"]["__VIEWSTATEGENERATOR"],
        '__EVENTVALIDATION': status["paramators"]["login"]["__EVENTVALIDATION"],
        'textBoxId': user_id,
        'textBoxPassword': password,
        'buttonLogin': 'ログイン'
    }

    res = session.post(url+path, data=params)
    if res.text.find(auth_invalid_message) > -1:
        sys.exit(auth_invalid_message)

    c = session.cookies.get("ASP.NET_SessionId")
    session_id = {"ASP.NET_SessionId": c}
    status["session"] = session_id

    status["login"]["userid"] = user_id
    status["login"]["password"] = password

    write_json(status, status_path)

    print("ログインしました ID: {}".format(user_id))

def genarate_project_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]
    project_info = [list(map(lambda td: td.text, row.find_all("td"))) for row in rows]

    return project_info

def list_project():
    path = "main/MyPage.aspx"

    status = read_json(status_path)
    header = status["session"]
    
    res = session.get(url+path, headers=header)
    html = res.text
    project_info = genarate_project_info(html)

    for (group, name, _, _, _) in project_info:
        print("{}@{}".format(name, group))

if __name__=="__main__":
    ld = LoginData()
    login(ld.user_id, ld.password)
    list_project()