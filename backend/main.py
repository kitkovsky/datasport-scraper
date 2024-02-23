import os
from typing import List

from dotenv import load_dotenv
from flask import Flask
from models import Base, Race
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_AUTH_TOKEN = os.getenv("DB_AUTH_TOKEN")

db_url = f"sqlite+{DB_URL}/?authToken={DB_AUTH_TOKEN}"

engine = create_engine(db_url, connect_args={"check_same_thread": False}, echo=True)
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
