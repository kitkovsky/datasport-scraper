import os
import sys
from typing import List

from flask import Flask

sys.path.append("..")

from db.connection import session
from db.models import Race

PORT = int(os.getenv("PORT", 8080))

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
    app.run(debug=True, host="0.0.0.0", port=PORT)
