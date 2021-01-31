from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import yaml

import bug_parser

with open('./config.yml', 'r') as f:
    config = yaml.safe_load(f)

ip = config['mongodb']['ip']
port = config['mongodb']['port']
user = config['mongodb']['user']
password = config['mongodb']['password']

client = MongoClient(f'mongodb://{user}:{password}@{ip}:{port}', serverSelectionTimeoutMS=5000)
db = client.bug_base
bug_collection = db.bug_collection


def get_mongo_data():
    try:
        return bug_collection.find_one()
    except ServerSelectionTimeoutError:
        return "Connection Timeout"


def get_data():
    if get_mongo_data() != "Connection Timeout" and get_mongo_data() is not None:
        mongo_data = get_mongo_data()
        fd_data = bug_parser.latest_bugs()
        devbug_date = mongo_data['DEVBUG']['created_at']
        supbug_date = mongo_data['SUPBUG']['created_at']
        cur_devbug_date = fd_data['DEVBUG']['created_at']
        cur_supbug_date = fd_data['SUPBUG']['created_at']
        if devbug_date != cur_devbug_date or supbug_date != cur_supbug_date:
            bug_collection.replace_one({'_id': mongo_data.get('_id')}, fd_data)
        return get_mongo_data()
    if get_mongo_data() is None:
        bugs = bug_collection.insert_one(bug_parser.latest_bugs()).inserted_id
        return bugs
    # if get_mongo_data() == "Connection Timeout":
    #    return bug_parser.latest_bugs()


if __name__ == "__main__":
    get_data()
