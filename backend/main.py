import os
from typing import List

from flask import Flask
from models import Base, Race
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

connection_string = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection_string, echo=True)
Base.metadata.create_all(bind=engine)

session = Session(engine)

app = Flask(__name__)


@app.route("/")
def root() -> str:
    return "hello there"


@app.route("/races")
def races() -> List[dict]:
    all_races = session.query(Race).all()
    return [race.to_dict_without_participants() for race in all_races]


@app.route("/races/<datasport_race_id>")
def race(datasport_race_id: int) -> dict | str:
    race = (
        session.query(Race).where(Race.datasport_race_id == datasport_race_id).first()
    )

    return race.to_dict() if race else "No race with this datasport race id exists"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
