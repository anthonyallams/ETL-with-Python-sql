import os
from dotenv import load_dotenv

load_dotenv()


DB_NAME = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')