from bs4 import BeautifulSoup
import sys

HIDDEN_PARAMS = [
    "__VIEWSTATE",
    "__VIEWSTATEGENERATOR",
    "__EVENTVALIDATION",
    "_ctl0:ContentPlaceHolder1:buttonAdd",
]


def __to_text(td):
    return td.text


def generate_hidden_params(html, request="POST"):
    soup = BeautifulSoup(html, "html.parser")
    if request == "POST":
        params = HIDDEN_PARAMS
    elif request == "LOGIN":
        params = HIDDEN_PARAMS[0:3]
        params.append("buttonLogin")
    data = {s: soup.find("input", attrs={"name": s}).get("value") for s in params}
    return data


def generate_project_info(html):
    soup = BeautifulSoup(html, "html.parser")

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})

    rows = table.find_all("tr")[1:]
    project_info = [list(map(__to_text, row.find_all("td")[:2])) for row in rows]

    return project_info


def generate_issues(html):
    soup = BeautifulSoup(html, "html.parser")

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})

    rows = table.find_all("tr")[2:-1]

    issues = [list(map(__to_text, row.find_all("td")[:7])) for row in rows]

    return issues


def find_board_id(html, name):
    soup = BeautifulSoup(html, "html.parser")

    TABLE_ID = "_ctl0_ContentPlaceHolder1_gridList"
    table = soup.find(attrs={"id": TABLE_ID})
    rows = table.find_all("tr")[1:]

    for row in rows:
        project_name = row.find_all("td")[1]
        if project_name.text == name:
            return project_name.a.get("href").split("=")[1]

    sys.exit("その名前のプロジェクトは存在しません")
