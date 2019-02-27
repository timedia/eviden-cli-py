import json
import os.path

JSON_PATH = os.path.join('.', 'json')
STATUS_PATH = os.path.join(JSON_PATH, 'state.json')

def write_json(data, path):
    json.dump(
        data,
        open(path, 'w'),
        ensure_ascii=False,
        indent=4,
        sort_keys=True,
        separators=(',', ': ')
    )

def read_json(file_path):
    return json.load(open(file_path, "r"))
