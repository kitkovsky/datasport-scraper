import os
from typing import List

import psycopg2
from flask import Flask
from orm.orm import Race, get_all_races

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
)

app = Flask(__name__)


@app.route("/")
def root():
    return "hello there"


@app.route("/races")
def races() -> List[Race]:
    return get_all_races(conn)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
