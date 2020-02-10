import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

ALLOWED_IDS = os.getenv('ALLOWED_IDS').split(',')

DB_CONNECTOR = os.getenv('DB_CONNECTOR')
