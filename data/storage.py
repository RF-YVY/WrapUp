import os
import json

data_file = os.path.join(os.path.expanduser("~"), ".weekly_report_data.json")

def save_data(data):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def clear_data():
    if os.path.exists(data_file):
        os.remove(data_file)
