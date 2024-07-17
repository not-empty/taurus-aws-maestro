from dotenv import load_dotenv
import json
import os

load_dotenv()

def load_config(file_path='config.json'):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

configuration = load_config()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

DEBUG_MODE = int(os.getenv('DEBUG_MODE'))

LOG_SCHEDULES = int(os.getenv('LOG_SCHEDULES'))
LOG_EVENTS = int(os.getenv('LOG_EVENTS'))
LOG_QUEUES = int(os.getenv('LOG_QUEUES'))
LOG_ACTIONS = int(os.getenv('LOG_ACTIONS'))

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_DB = int(os.getenv('REDIS_DB'))

SAVE_DB_HISTORY = int(os.getenv('SAVE_DB_HISTORY'))

TIME_SCAN_QUEUE_SCHEDULE = int(os.getenv('TIME_SCAN_QUEUE_SCHEDULE'))
TIME_SCAN_EC2_STARTED_SCHEDULE = int(os.getenv('TIME_SCAN_EC2_STARTED_SCHEDULE'))
TIME_SCAN_EC2_STOPPED_SCHEDULE = int(os.getenv('TIME_SCAN_EC2_STOPPED_SCHEDULE'))
TIME_SCAN_API_HEALTHCHECK_SCHEDULE = int(os.getenv('TIME_SCAN_API_HEALTHCHECK_SCHEDULE'))