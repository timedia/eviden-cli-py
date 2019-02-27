import requests
from jsonio import read_json, write_json, config_path, status_path
from setting import LoginData

data = LoginData()

# requests でログインしてセッションクッキーを作る
session = requests.session()

status = read_json(status_path)
login_data = {
    '__VIEWSTATE': status["paramators"]["login"]["__VIEWSTATE"],
    '__VIEWSTATEGENERATOR': status["paramators"]["login"]["__VIEWSTATEGENERATOR"],
    '__EVENTVALIDATION': status["paramators"]["login"]["__EVENTVALIDATION"],
    'textBoxId': data.user_id,
    'textBoxPassword': data.password+"hoge",
    'buttonLogin': 'ログイン'
}

res = session.post('https://etrack.timedia.co.jp/EasyTracker/Login.aspx', data=login_data)

print(res.text)