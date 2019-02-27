import json
import os.path

json_path = os.path.join('.', 'json')
config_path = os.path.join(json_path, 'config.json')
status_path = os.path.join(json_path, 'state.json')

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
