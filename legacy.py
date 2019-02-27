import requests
from bs4 import BeautifulSoup
import sys

from jsonio import read_json, write_json, config_path, status_path

url = "https://etrack.timedia.co.jp/EasyTracker/"

auth_invalid_message = 'ログインID、メールアドレスもしくはパスワードが間違っています' 
auth_empty_message = 'ログインID(またはメールアドレス)とパスワードを入力してください'

def login_request(userid, password):
    path = "Login.aspx"

    status = read_json(status_path)
    params = {
        '__VIEWSTATE': status["paramators"]["login"]["__VIEWSTATE"],
        '__VIEWSTATEGENERATOR': status["paramators"]["login"]["__VIEWSTATEGENERATOR"],
        '__EVENTVALIDATION': status["paramators"]["login"]["__EVENTVALIDATION"],
        'textBoxId': status["login"]["userid"],
        'textBoxPassword': status["login"]["password"],
        'buttonLogin': 'ログイン'
    }

    res = requests.post(url+path, data=params)
    is_authenticated = res.text.find(auth_invalid_message) + res.text.find(auth_empty_message) is -2
    return res, is_authenticated

def login(userid, password):
    res, is_authenticated = login_request(userid, password)

    auth_data = {"userid": "", "password": ""}

    if is_authenticated:
        # success
        print("logined: "+userid)
        auth_data["userid"] = userid
        auth_data["password"] = password

        soup = BeautifulSoup(res.text, 'html.parser')
        status = read_json(status_path)

        status["projcet"]["__VIEWSTATE"] = soup.form.find("input", id="__VIEWSTATE")
        status["projcet"]["__VIEWSTATEGENERATOR"] = soup.form.find("input", id="__VIEWSTATEGENERATOR")
        status["projcet"]["__EVENTVALIDATION"] = soup.form.find("input", id="__EVENTVALIDATION")

        write_json(auth_data, config_path)
        write_json(status, status_path)
    else:
        # fault
        print('ログインIDもしくはパスワードに不備があります')
        write_json(auth_data, config_path)

def is_loggined():
    config = read_json(config_path)
    return (config["userid"] != "" and config["password"] != "")

def altlogin():
    config = read_json(config_path)
    res, is_authenticated = login_request(config["userid"], config["password"])
    if is_authenticated:
        return res
    else:
        sys.exit('ログインし直してください')

def genarate_project_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]
    project_info = [list(map(lambda td: td.text, row.find_all("td"))) for row in rows]

    return project_info

def list_project():
    res = altlogin()
    html = res.text
    project_info = genarate_project_info(html)

    for (group, name, _, _, _) in project_info:
        print("{}@{}".format(name, group))

def select_project(project_name):
    pass

if __name__=="__main__":
    # コマンドライン引数でtry-exceptするべき
    command = sys.argv[1]
    args = sys.argv[2:]

    # 引数のvalidationをしてから実行？
    if command == "--login":
        userid, password = args[:2]
        login(userid, password)
    elif command == "--list":
        list_project()
    elif command == "--select":
        name = args[0]
        select_project(name)