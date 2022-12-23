from flask import current_app
from api.lib.settings import DB_NAME, DB_USER,TEST_DB_NAME, TEST_DB_USER, SINGLE_URL, BATCH_URL
from flask import g
import psycopg2

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER)

test_conn = psycopg2.connect(dbname = TEST_DB_NAME, user = TEST_DB_USER)
test_cursor = test_conn.cursor()

cursor = conn.cursor()

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(user = current_app.config['DB_USER'],
                password = current_app.config['DB_PASSWORD'],
            dbname = current_app.config['DATABASE'])
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()