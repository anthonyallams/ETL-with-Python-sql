import os
from dotenv import load_dotenv

load_dotenv()


DB_NAME = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')
TEST_DB_NAME = os.getenv('TEST_DB_NAME')
TEST_DB_USER = os.getenv('TEST_DB_USER')
SINGLE_URL = os.getenv('SINGLE_URL')
BATCH_URL = os.getenv('BATCH_URL')