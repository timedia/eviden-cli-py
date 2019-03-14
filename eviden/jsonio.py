import json
import os.path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_PATH = os.path.join(PROJECT_ROOT, 'json', 'status.json')


def write_json(data, path):
    o = open(path, 'w')
    json.dump(
        data,
        o,
        ensure_ascii=False,
        indent=4,
        sort_keys=True,
        separators=(',', ': ')
    )
    o.close()


def read_json(file_path):
    o = open(file_path, "r")
    data = json.load(o)
    o.close()
    return data


def read_cookie():
    status = read_json(STATUS_PATH)
    return status["session"]


def write_cookie(session_id):
    status = read_json(STATUS_PATH)
    status["session"] = session_id
    write_json(status, STATUS_PATH)
