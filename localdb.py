import sqlite3

from flask import Flask, g

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('provider.db')

    return db


@app.teardown_appcontext
def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()





