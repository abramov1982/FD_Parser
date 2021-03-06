import tickets_to_mongo
import time
import yaml

with open('./config.yml', 'r') as f:
    config = yaml.safe_load(f)

request_period = config['request_period']


def timer(seconds):
    tickets_to_mongo.add_db_tickets()
    time.sleep(seconds)
    timer(request_period)


if __name__ == "__main__":
    timer(request_period)
