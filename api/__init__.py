from flask import Flask,jsonify
from api.lib.db import conn
from api.models.article import Article
from api.lib.helper import build_from_record, build_from_records
from api.lib.settings import DB_NAME, DB_USER
import psycopg2

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return 'Welcome'


    @app.route('/articles')
    def articles():
        cursor = conn.cursor()
        query = ("SELECT * from articles limit 10")
        cursor.execute(query)
        all_records = cursor.fetchall()
        records = build_from_records(Article, all_records)
        article_records = [article.__dict__ for article in records]
        return jsonify(article_records)


    @app.route('/article/<int:id>')
    def article(id):
        cursor = conn.cursor()
        query = ("SELECT * from articles where id = %s")
        cursor.execute(query,(id,))
        record = cursor.fetchone()
        article_record = build_from_record(Article, record)
        return jsonify(article_record.__dict__)   

    return app
