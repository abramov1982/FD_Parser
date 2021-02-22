import json
import yaml
from datetime import datetime
from pymongo import DESCENDING
from pymongo import MongoClient

from dateutil.relativedelta import *

with open('../config.yml', 'r') as f:
    config = yaml.safe_load(f)

ip = config['mongodb']['ip']
port = config['mongodb']['port']
db_user = config['mongodb']['db_user']
db_password = config['mongodb']['db_password']
dbname = config['mongodb']['dbname']
bug_types = config['bug_types']

client = MongoClient(f'mongodb://{db_user}:{db_password}@{ip}:{port}')
db = client[dbname]


def get_last_bug(bug_type):
    cursor = db[f'{bug_type}'].find().sort('created_at', DESCENDING).limit(1)
    for cur in cursor:
        return cur


def get_bot_message(bug_type):
    data = get_last_bug(bug_type)
    message = f"Последний {bug_type}\n" \
              f"Тикет - {data['ticket_id']}\n" \
              f"СТП - {data['agent_name']}\n" \
              f"Заказчик - {data['customer_name']}\n" \
              f"Дата - {data['created_at']}"
    return message


def get_statistic():
    now = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    message = ''
    for bug_type in bug_types:
        bug = get_last_bug(bug_type)
        bug_date = datetime.strptime(bug['created_at'].strftime('%Y-%m-%d'), '%Y-%m-%d')
        time_delta = abs((now-bug_date).days)
        string = f"Дней без {bug_type} - {time_delta}\n"
        message += string
    return message


