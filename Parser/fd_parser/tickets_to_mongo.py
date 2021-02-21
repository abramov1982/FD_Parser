from dateutil import parser as psr
from dateutil.relativedelta import *
from datetime import *
import json
import requests
from pymongo import MongoClient
import yaml

with open('./config.yml', 'r') as f:
    config = yaml.safe_load(f)

api_key = config['fd_api']['api_key']
api_password = config['fd_api']['password']
domain = config['fd_api']['domain']
pages = config['fd_api']['pages']
tickets_slug = '/helpdesk/tickets'
ip = config['mongodb']['ip']
port = config['mongodb']['port']
db_user = config['mongodb']['db_user']
db_password = config['mongodb']['db_password']
dbname = config['mongodb']['dbname']
bug_types = config['bug_types']
delta = config['search_delta']

client = MongoClient(f'mongodb://{db_user}:{db_password}@{ip}:{port}')
db = client[dbname]


# Получение списка состоящего из номеров тикетов в количестве page_quantity страниц
def get_tickets_id(page_quantity=1):
    data = []
    start_date = datetime.now()-relativedelta(months=+delta)
    try:
        for page in range(1, page_quantity + 1):
            r = requests.get(f"{domain}{tickets_slug}/view/351659?format=json&page={page}",
                             auth=(api_key, api_password))
            if r.status_code == 200:
                data += json.loads(r.content)
            else:
                pass
    except requests.exceptions.ConnectionError:
        pass
    ticket_ids = [i['display_id'] for i in data if psr.parse(i['created_at'], ignoretz=True) > start_date]
    return ticket_ids


# Выборка последней записи с багом из логгирования времени по заявке. Используется в get_ticket_notes
def bug_sort(bug_type, primary_dict, secondary_dict):
    if bug_type in primary_dict and primary_dict[bug_type]['created_at'] < secondary_dict['created_at']:
        primary_dict[bug_type] = secondary_dict
    elif bug_type not in primary_dict:
        primary_dict[bug_type] = secondary_dict


# Проверка тикета на наличие записей о багах. Возвращает словарь с типом/типами багов и информацией о них
def get_ticket_notes(ticket_id):
    notes = {}
    r = requests.get(f"{domain}{tickets_slug}/{ticket_id}/time_sheets.json?billable=false",
                     auth=(api_key, api_password))
    response = json.loads(r.content)
    for i in response:
        note_date = psr.parse(i['time_entry']['created_at'], ignoretz=True)
        note = {'ticket_id': i['time_entry']['ticket_id'],
                'created_at': note_date,
                'agent_name': i['time_entry']['agent_name'],
                'customer_name': i['time_entry']['customer_name'],
                'note': i['time_entry']['note']}
        for bug_type in bug_types:
            try:
                if set(i['time_entry']['note']) is not None:
                    if set(i['time_entry']['note'].split()) & {bug_type}:
                        bug_sort(bug_type, notes, note)
            except TypeError:
                pass
    return notes


# Добавление тикетов и и информации о них в БД.
def add_db_tickets():
    tickets_in_db = []

    # Запись в tickets_in_db номеров которые уже есть в БД
    for bug in bug_types:
        cursor = db[f'{bug}'].find({}, {'ticket_id': 1})
        tickets_in_db += [cur['ticket_id'] for cur in cursor]

    # Генерация списка тикетов для проверки, с исключением тикетов которые уже в БД
    tickets_to_check = [i for i in get_tickets_id(page_quantity=pages) if i not in tickets_in_db]

    # Проверка тикета на баги и добавление в БД
    for ticket in tickets_to_check:
        note = get_ticket_notes(ticket)
        if note:
            for key, value in note.items():
                collection = db[f'{key}']
                collection.insert_one(value)


if __name__ == "__main__":
    add_db_tickets()
