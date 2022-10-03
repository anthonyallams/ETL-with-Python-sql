from api.lib.settings import DB_NAME, DB_USER
import psycopg2

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER)

cursor = conn.cursor()