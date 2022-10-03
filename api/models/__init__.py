from flask import Flask,jsonify
from api.lib.db import conn
from api.models.article import Article
from api.lib.settings import DB_NAME, DB_USER
import psycopg2

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return 'Overtone DB Connection'

    @app.route('/articles')
    def articles():
        cursor = conn.cursor()
        query = ("SELECT * from articles limit 10")
        cursor.execute(query)
        articles_record = cursor.fetchall()
        return jsonify(articles_record)

    @app.route('/article/<int:id>')
    def article(id):
        cursor = conn.cursor()
        query = ("SELECT * from articles where id = %s")
        cursor.execute(query,(id,))
        article_record = cursor.fetchone()
        return jsonify(article_record)   

    return app
