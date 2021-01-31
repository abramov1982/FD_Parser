from dateutil import parser as psr
import json
import requests
import yaml


with open('./config.yml', 'r') as f:
    config = yaml.safe_load(f)

api_key = config['fd_api']['api_key']
password = config['fd_api']['password']
domain = config['fd_api']['domain']
tickets_slug = '/helpdesk/tickets'


def get_tickets(page_quantity=1):
    data = []
    try:
        for i in range(1, page_quantity + 1):
            # r = requests.get(f"{domain}{tickets_slug}"
            #                  f"/filter/all_tickets?format=json&wf_order=updated_at&"
            #                  f"wf_order_type=desc&wf_order=due_by&wf_order_type=asc&page={i}",
            #                  auth=(api_key, password))
            r = requests.get(f"{domain}{tickets_slug}/view/351659?format=json&page={i}", auth=(api_key, password))
            if r.status_code == 200:
                data += json.loads(r.content)
            else:
                pass
        return data
    except requests.exceptions.ConnectionError:
        return data


def get_tickets_id(tickets):
    ticket_ids = []
    if tickets:
        ticket_ids += [i['display_id'] for i in tickets]
    return ticket_ids


def bug_sort(bug_type, primary_dict, secondary_dict):
    if bug_type in primary_dict and primary_dict[bug_type]['created_at'] < secondary_dict['created_at']:
        primary_dict[bug_type] = secondary_dict
    elif bug_type not in primary_dict:
        primary_dict[bug_type] = secondary_dict


def get_ticket_notes(ticket_id):
    notes = {}
    r = requests.get(f"{domain}{tickets_slug}/{ticket_id}/time_sheets.json?billable=false", auth=(api_key, password))
    response = json.loads(r.content)
    for i in response:
        note_date = psr.parse(i['time_entry']['created_at'], ignoretz=True)
        note = {'ticket_id': i['time_entry']['ticket_id'],
                'created_at': note_date,
                'agent_name': i['time_entry']['agent_name'],
                'customer_name': i['time_entry']['customer_name'],
                'note': i['time_entry']['note']}

        if set(i['time_entry']['note'].split()) & {'SUPBUG'}:
            bug_sort('SUPBUG', notes, note)
        if set(i['time_entry']['note'].split()) & {'DEVBUG'}:
            bug_sort('DEVBUG', notes, note)
    return notes


def latest_bugs(page_quantity=1):
    bugs = {}
    for i in get_tickets_id(get_tickets(page_quantity=page_quantity)):
        ticket_info = get_ticket_notes(i)
        if 'DEVBUG' in ticket_info:
            devbug_info = ticket_info['DEVBUG']
            bug_sort('DEVBUG', bugs, devbug_info)
        if 'SUPBUG' in ticket_info:
            supbug_info = ticket_info['SUPBUG']
            bug_sort('SUPBUG', bugs, supbug_info)
    return bugs
